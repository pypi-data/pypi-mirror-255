from spark_batch.lib.spark_session import get_spark_session
from spark_batch.lib.elt_manager import EltManager
import argparse, os

def main():
    parser = argparse.ArgumentParser(description="ETL process with options for ingest_full, and ingest_increment.")
    
    subparsers = parser.add_subparsers(dest="subcommand", help="Choose one of the following subcommands.")

    # Subparser for ingest_full
    ingest_full_parser = subparsers.add_parser("ingest_full")
    ingest_full_parser.add_argument("--config", required=True, help="Path to the config file")
    ingest_full_parser.add_argument("--source_type", required=True, help="Source type (e.g., oracle)")
    ingest_full_parser.add_argument("--source_topic", required=True, help="Source topic (e.g., bcparking)")
    ingest_full_parser.add_argument("--target_type", required=True, help="Target type (e.g., delta)")
    ingest_full_parser.add_argument("--target_topic", required=True, help="Target topic (e.g., bronze-bcparking)")
    ingest_full_parser.add_argument("--source_objects", required=True, nargs="+", help="Source objects (e.g., tb_tminout)")
    ingest_full_parser.add_argument("--target_object", required=True, help="Target object (e.g., tb_tminout)")
    ingest_full_parser.add_argument("--source_inc_query", required=False, help="Source increment query")
    ingest_full_parser.add_argument("--batch_size", type=int, default=500000, help="Batch size for init_rsm")

    # Subparser for ingest_increment
    ingest_increment_parser = subparsers.add_parser("ingest_increment")
    ingest_increment_parser.add_argument("--config", required=True, help="Path to the config file")
    ingest_increment_parser.add_argument("--source_type", required=True, help="Source type (e.g., oracle)")
    ingest_increment_parser.add_argument("--source_topic", required=True, help="Source topic (e.g., bcparking)")
    ingest_increment_parser.add_argument("--target_type", required=True, help="Target type (e.g., delta)")
    ingest_increment_parser.add_argument("--target_topic", required=True, help="Target topic (e.g., bronze-bcparking)")
    ingest_increment_parser.add_argument("--source_objects", required=True, nargs="+", help="Source objects (e.g., tb_tminout)")
    ingest_increment_parser.add_argument("--target_object", required=True, help="Target object (e.g., tb_tminout)")
    ingest_increment_parser.add_argument("--from_date", required=True, help="Start date for incremental load")
    ingest_increment_parser.add_argument("--to_date", required=True, help="End date for incremental load")
    ingest_increment_parser.add_argument("--source_inc_query", required=True, help="Source increment query")
    ingest_increment_parser.add_argument("--target_condition", required=True, help="Target condition")
    ingest_increment_parser.add_argument("--batch_size", type=int, default=500000, help="Batch size for init_rsm")


    args = parser.parse_args()

    # Read the configuration file
    if not os.path.isfile(args.config):
        print(f"Configuration file not found: {args.config}")
        return
    
    spark = get_spark_session("elt")
    em = EltManager(spark, args.config)

    if args.subcommand == "ingest_full":
        em.init_rsm(args.source_type, args.source_topic, args.target_type, args.target_topic, args.batch_size)

        source_df, target_df, valid = em.ingest_full(args.source_objects, args.target_object)
        return (source_df, target_df, valid)
    
    elif args.subcommand == "ingest_increment":
        em.init_rsm(args.source_type, args.source_topic, args.target_type, args.target_topic, args.batch_size)

        source_inc_query = args.source_inc_query
        target_condition = args.target_condition
        source_df, target_df, valid = em.ingest_increment(args.source_objects, args.target_object, source_inc_query, target_condition)
        return (source_df, target_df, valid)        

if __name__ == "__main__":
    source_df, target_df, valid = main()
    print("success=", valid, "(source: ", source_df.count(), ", target:", target_df.filter(target_condition).count(), ")")

# spark-submit --properties-file  ~/work/conf/spark.properties run.py ingest_full --config lib/config.yaml --source_type oracle1 --source_topic bcparking --target_type delta1 --target_topic bronze-bcparking --source_objects tb_tmparking --target_object tb_tmparking --batch_size 500000

# spark-submit --properties-file  ~/work/conf/spark.properties run.py ingest_increment --config lib/config.yaml --source_type oracle1 --source_topic bcparking --target_type delta1 --target_topic bronze-bcparking --source_objects tb_tmparking --target_object tb_tmparking --batch_size 500000 --source_inc_query "SELECT * FROM bcparking.tb_tminout WHERE in_dttm >= TO_DATE('{from}', 'YYYYMMDD') AND in_dttm < TO_DATE('{to}', 'YYYYMMDD')" --target_condition "in_dttm >= DATE '{from}' AND in_dttm < DATE '{to}'" --from_date="20230601" --to_date="20230602"

# spark-submit --properties-file  ~/work/conf/spark.properties run.py ingest_increment --config lib/config.yaml --source_type oracle1 --source_topic bcparking --target_type delta1 --target_topic bronze-bcparking --source_objects tb_tmparking --target_object tb_tmparking --batch_size 500000 --source_inc_query "SELECT * FROM bcparking.tb_tminout WHERE in_dttm >= TO_DATE('20230601', 'YYYYMMDD') AND in_dttm < TO_DATE('20230602', 'YYYYMMDD')" --target_condition "where reg_dttm >= DATE '2023-06-01' AND reg_dttm < DATE '2023-06-02'" --from_date="20230601" --to_date="20230602"
