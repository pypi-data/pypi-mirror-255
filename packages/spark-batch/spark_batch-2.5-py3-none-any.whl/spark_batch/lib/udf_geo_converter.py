from shapely.geometry import Point
from pyproj import Transformer
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import geopandas as gpd
import os

class GeoConverter(object):

    def __init__(self, shp="hadm"): #, shp_file_path=None, dbf_file_path=None):

        if not (shp =="hadm" or shp =="badm" or shp == "hadm2024" or shp == "badm2024"):
            print("shp argument error : should be 'hadm', 'badm', 'hadm2024', 'badm2024'")
            return 

        # 좌표계 정의
        self.epsg5186 = Transformer.from_crs("epsg:5186", "epsg:4326", always_xy=True)
        self.wgs84 = Transformer.from_crs("epsg:4326", "epsg:5186", always_xy=True)

        pwd = os.path.dirname(os.path.abspath(__file__))
        shp_file_path = os.path.join(pwd, self._get_geo_path(shp) + ".shp")
        dbf_file_path = os.path.join(pwd, self._get_geo_path(shp) + ".dbf")

        # 데이터 로드
        self.load_data(shp_file_path, dbf_file_path)

    def _get_geo_path(self, shp):
        if shp == 'hadm':
            self.infoKey = 'HJD_NAM_left'
            return "../data/shp/BML_HADM_AS"
        elif shp == "badm":
            self.infoKey = 'BJD_NAM_left'
            return "../data/shp/BML_BADM_AS"
        elif shp == 'hadm2024':
            self.infoKey = 'HJD_NAM_left'
            return "../data/shp2024/BML_HADM_AS"
        elif shp == "badm2024":
            self.infoKey = 'BJD_NAM_left'
            return "../data/shp2024/BML_BADM_AS"

        return None


    def load_data(self, shp_file_path, dbf_file_path):
        # SHP 파일과 DBF 파일 읽기
        self.gdf = gpd.read_file(shp_file_path)
        df_dbf = gpd.read_file(dbf_file_path)

        # 동 정보를 가진 DBF 파일과 SHP 파일을 조인
        self.merged_gdf = self.gdf.merge(df_dbf, left_index=True, right_index=True, how='left',
                                         suffixes=('_left', '_right'))

    def to_float(self, value):
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
                print(f"값을 숫자로 변환하는데 실패했습니다: {value}")
        return value

    # XY 좌표를 동 이름으로 변환하는 함수
    def epsg5186_to_dong(self, lon, lat):
        lon = self.to_float(lon)
        lat = self.to_float(lat)

        if lon is None or lat is None:
            return None

        point = Point(lon, lat)
        dong = None
        try:
        #nearest_row = merged_gdf.iloc[(merged_gdf['geometry_left'].distance(Point(longitude, latitude))).idxmin()]
            nearest_row = self.merged_gdf.iloc[(self.merged_gdf['geometry_left'].apply(lambda geom: point.distance(geom))).idxmin()]
            if not nearest_row['geometry_left'].contains(point):
                raise ValueError("Error: 해당 좌표에 대응하는 지오메트리가 없습니다.")
            dong = nearest_row[self.infoKey] #'HJD_NAM_left']  # 'FTR_CDE_left'는 동 정보를 가리키는 열의 이름으로 수정
        except ValueError:
            dong = None # print("Error: 해당 좌표에 대응하는 지오메트리가 없습니다.")
        return dong

    def wsg84_to_dong(self, lon, lat):
        lon = self.to_float(lon)
        lat = self.to_float(lat)

        if lon is None or lat is None:
            return None

        x, y = self.wsg84_transform(lon, lat) # WSG84 >
        return self.epsg5186_to_dong(x, y)

    def wsg84_transform(self, lon, lat):
        lon = self.to_float(lon)
        lat = self.to_float(lat)

        if lon is None or lat is None:
            return None

        x, y = self.wgs84.transform(lon, lat)
        return x, y

    def epsg5186_transform(self, lon, lat):
        lon = self.to_float(lon)
        lat = self.to_float(lat)

        if lon is None or lat is None:
            return None

        x, y = self.epsg5186.transform(lon, lat)
        return x, y

    def regist(self, spark):
        # UDF 등록
        epsg5186_to_dong = udf(self.epsg5186_to_dong, StringType())
        wsg84_to_dong = udf(self.wsg84_to_dong, StringType())

        spark.udf.register("epsg5186_to_dong", epsg5186_to_dong)
        spark.udf.register("wsg84_to_dong", wsg84_to_dong)

        return (epsg5186_to_dong,  wsg84_to_dong)


#    def print_test(self):
#        seoul = (126.9784, 37.5665)
#        dong = self.wsg84_to_dong(*seoul)
#        print(f"The dong is: {dong}")
#
#        dong = self.wsg84_to_dong(126.771, 37.512)
#        print(f"The dong is: {dong}")
#
#        dong = self.wsg84_to_dong(126.770701, 37.542777)
#        print(f"The dong is: {dong}")
#
#
#    def print_shp(self):
#        print(f"Coordinate Data: ")
#        size = len(self.gdf['geometry'].centroid.x.iloc[:])
#        for i in range(0, size):
#            lon = self.gdf['geometry'].centroid.x.iloc[i]
#            lat = self.gdf['geometry'].centroid.y.iloc[i]
#            dong = self.epsg5186_to_dong(lon, lat)
#
#            x, y = self.epsg5186_transform(lon, lat)
#            print(f"  {dong} ({lon}, {lat}), ({x}, {y})")
#
#geo = GeoConverter("hadm")
#geo.print_shp()
#
#geo = GeoConverter("badm")
#geo.print_shp()
#
#geo = GeoConverter("hadm2024")
#geo.print_shp()
#
#geo = GeoConverter("badm2024")
#geo.print_shp()

#geo = GeoConverter("badm2023")
#geo = GeoConverter("badm2023")
#geo.print_shp()
#
#
#    def test(self):
#        # 사용 예제
#        shp_file_path = "geodata/shp/BML_HADM_AS.shp"
#        dbf_file_path = "geodata/shp/BML_HADM_AS.dbf"
#
#        geo_processor = GeoDataProcessor(shp_file_path, dbf_file_path)
#        geo_processor.print_test()
#        geo_processor.print_shp()
