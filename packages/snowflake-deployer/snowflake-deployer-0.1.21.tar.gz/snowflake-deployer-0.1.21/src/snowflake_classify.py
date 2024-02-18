from src.configurator.configurator import configurator
from src.snowflake.snowflake_client import snowflake_client as sf_client
from src.yaml_writer.yaml_writer import yaml_writer
from src.deploy_logger.logger import deploy_logger
from src.wrangler.wrangler import wrangler
import threading
from time import sleep
import time
from src.util.util import remove_prefix
import traceback

def classify_object(semaphore, logger, sf, writer, wrangle, full_object_name:str, database_name:str, schema_name:str, object_name:str, tags_database_name:str, tags_schema_name:str, env_database_prefix:str, max_sample_size:int):
    # full object name includes the database prefix
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')
            
            # Run classification for a specific table
            data = sf.object_classify(full_object_name, max_sample_size)
            
            # Loop through Classification results to get into format for the writer
            columns = []
            tag_db_name = remove_prefix(tags_database_name,env_database_prefix)
            for col in data:
                
                sensitivity_key = wrangle.create_jinja_ref(tag_db_name, tags_schema_name, 'SENSITIVITY')
                sensitivity_value = col['TAG_SENSITIVITY']
                semantic_key = wrangle.create_jinja_ref(tag_db_name, tags_schema_name, 'SEMANTIC')
                semantic_value = col['SEMANTIC_CATEGORY']
                classification_category_key = wrangle.create_jinja_ref(tag_db_name, tags_schema_name, 'CLASSIFICATION_CATEGORY')
                classification_category_value = col['PRIVACY_CATEGORY']
                classification_probability_key = wrangle.create_jinja_ref(tag_db_name, tags_schema_name, 'CLASSIFICATION_PROBABILITY')
                classification_probability_value = col['PROBABILITY']
                classified_key = wrangle.create_jinja_ref(tag_db_name, tags_schema_name, 'CLASSIFIED')
                classified_value = 'Y'

                c = {}
                c['NAME'] = col['COLUMN_NAME']
                ctags = []
                remove_tags = []
                ctags.append({classified_key:classified_value})
                if sensitivity_value != 'INTERNAL':
                    ctags.append({sensitivity_key:sensitivity_value})
                    ctags.append({semantic_key:semantic_value})
                    ctags.append({classification_category_key:classification_category_value})
                    ctags.append({classification_probability_key:classification_probability_value})
                else:
                    remove_tags.append(sensitivity_key)

                c['TAGS'] = ctags
                c['TAGS_TO_REMOVE'] = remove_tags
                columns.append(c)
            d = {}
            d['COLUMNS'] = columns
            d['OBJECT_NAME'] = object_name

            ##############################################
            #               Write data - OBJECTS
            ##############################################

            db_name_sans_prefix = remove_prefix(database_name,env_database_prefix)
            
            # OBJECT DB 
            db = {}
            db['DATABASE_NAME_SANS_ENV'] = db_name_sans_prefix
            db_ignore_existing = True
            writer.write_database_file(db, db_ignore_existing)

            # OBJECT SCHEMA
            schema = {}
            schema['SCHEMA_NAME'] = schema_name
            schema_ignore_existing = True
            writer.write_schema_file(db_name_sans_prefix, schema, schema_ignore_existing)

            # Object
            object_metadata_only = True
            writer.write_object_file(db_name_sans_prefix, schema_name, d, object_metadata_only, False)
            
            msg = 'classified (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def snowflake_classify(args:dict):
    start_time = time.time()

    logger = deploy_logger('info')

    conf = configurator(args)
    config = conf.get_config()
    default_owner = config['DEPLOY_ROLE']

    try:
        logger.log('','Connecting to Snowflake')
        sf = sf_client(config['SNOWFLAKE_PRIVATE_KEY'], config['SNOWFLAKE_PRIVATE_KEY_PASSWORD'], config['SNOWFLAKE_ACCOUNT'], config['SNOWFLAKE_USERNAME'], config['SNOWFLAKE_WAREHOUSE'], config['database'], config['schema'] )
        wrangle = wrangler(sf)
        writer = yaml_writer()
        logger.log('','Connected')

        semaphore = threading.Semaphore(config['MAX_THREADS'])
 
        # determine list of databases to check based on env
        if config['CLASSIFY_DATABASES'] != []:
            classify_databases = config['CLASSIFY_DATABASES'] # the configurator adds the prefix so these include the prefix name
        else:
            classify_databases = sf.databases_get(config['ENV_DATABASE_PREFIX']) # this returns with the prefix on the db name

        # get list of objects to classify 
        logger.log('','Getting objects to classify')
        objects_to_classify = sf.objects_to_classify(classify_databases, config['CLASSIFY_TAGS_DB'], config['CLASSIFY_TAGS_SCHEMA'])
        #print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        #print(objects_to_classify)
        #print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        # loop and run classification SQL (get from DI code)

        if(len(objects_to_classify) > 0):
            tags_db_name = config['CLASSIFY_TAGS_DB']
            tags_schema_name = config['CLASSIFY_TAGS_SCHEMA']
            env_database_prefix = config['ENV_DATABASE_PREFIX']
            ##############################################
            #               Write data - TAGS
            ##############################################

            db_name_sans_prefix = remove_prefix(tags_db_name,env_database_prefix)
            ignore_existing = True

            # TAG DB 
            db = {}
            db['DATABASE_NAME_SANS_ENV'] = db_name_sans_prefix
            writer.write_database_file(db, ignore_existing)

            # TAG SCHEMA
            schema = {}
            schema['SCHEMA_NAME'] = tags_schema_name
            writer.write_schema_file(db_name_sans_prefix, schema, ignore_existing)

            tag = {}
            tag['TAG_NAME'] = 'SENSITIVITY'
            tag['OWNER'] = default_owner
            writer.write_tag_file(db_name_sans_prefix, tags_schema_name, tag, ignore_existing)

            tag = {}
            tag['TAG_NAME'] = 'SEMANTIC'
            tag['OWNER'] = default_owner
            writer.write_tag_file(db_name_sans_prefix, tags_schema_name, tag, ignore_existing)

            tag = {}
            tag['TAG_NAME'] = 'CLASSIFICATION_CATEGORY'
            tag['OWNER'] = default_owner
            writer.write_tag_file(db_name_sans_prefix, tags_schema_name, tag, ignore_existing)

            tag = {}
            tag['TAG_NAME'] = 'CLASSIFICATION_PROBABILITY'
            tag['OWNER'] = default_owner
            writer.write_tag_file(db_name_sans_prefix, tags_schema_name, tag, ignore_existing)

            tag = {}
            tag['TAG_NAME'] = 'CLASSIFIED'
            tag['OWNER'] = default_owner
            writer.write_tag_file(db_name_sans_prefix, tags_schema_name, tag, ignore_existing)


        threads = []
        max_sample_size = int(config['CLASSIFY_MAX_SAMPLE_SIZE'])
        for obj in objects_to_classify:
            full_object_name = obj['FULL_OBJECT_NAME']
            tnr = full_object_name
            database_name = obj['DATABASE_NAME']
            schema_name = obj['SCHEMA_NAME']
            object_name = obj['OBJECT_NAME']

            t = threading.Thread(target=classify_object, name=tnr, args=(semaphore, logger, sf, writer, wrangle, full_object_name, database_name, schema_name, object_name, config['CLASSIFY_TAGS_DB'], config['CLASSIFY_TAGS_SCHEMA'], config['ENV_DATABASE_PREFIX'], max_sample_size))
            threads.append(t)

        # Kick off all threads to begin execution
        for t in threads:
            t.start()

        # if threads are not joined, the script will continue to run while the threads are also running.
        # Joining the threads means we will wait here until all the threads are done processing before continuing
        for t in threads:
            t.join()

        # Wait till all threads have finished
        while len(threading.enumerate()) > 1:
            #print(len(threading.enumerate()))
            sleep(1)
  
        logger.log('','all objects have been classified')
        msg = "--- Executed in %s seconds ---" % (round(time.time() - start_time,1))
        logger.log('',msg)

    except Exception as ex:
        traceback_text = traceback.format_exc() # get error traceback
        msg = 'error - see error log at end'
        logger.log('',msg)
        logger.log_error(str(ex), 'script', traceback_text)

    finally:
        if 'sf' in locals() or 'sf' in globals():
            del sf

        error_count = logger.get_error_count()
        if error_count > 0:
            logger.show_all_errors()
            raise Exception("Errors occured - see log for details")
        else:
            logger.log('','No errors! Nice job!')