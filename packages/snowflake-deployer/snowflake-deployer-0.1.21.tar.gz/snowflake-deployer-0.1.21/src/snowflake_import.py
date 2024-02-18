import os
from src.configurator.configurator import configurator
from src.snowflake.snowflake_client import snowflake_client as sf_client
from src.yaml_writer.yaml_writer import yaml_writer
from src.deploy_logger.logger import deploy_logger
from src.wrangler.wrangler import wrangler
import logging
#import warnings
#warnings.simplefilter("ignore")
import threading
from time import sleep
import time
import traceback
import queue

def task_warehouse(semaphore, writer, sf, config:dict, tn:str, wh:dict, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')
            writer.write_warehouse_file(wh)
            
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def task_role(semaphore, writer, sf, config:dict, tn:str, r:dict, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')
            #logQueue.put_nowait((thread_name,'Start'))
            writer.write_role_file(r)

            #print(f'Thread {name} End')
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            #logQueue.put_nowait((thread_name,msg))
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def task_db(semaphore, writer, sf, config:dict, tn:str, db:dict, current_role:str, available_roles:list, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')

            writer.write_database_file(db)
            
            threads_list = []
            #####################################################
            # Schemas
            #schemas = sf.schemas_get(db['DATABASE_NAME'],config['DEPLOY_DATABASE_NAME'],config['ENV_DATABASE_PREFIX'], current_role, available_roles, ignore_roles_list)
            schemas = []
            if not config['IMPORT_OBJECT_TYPES'] or 'SCHEMA' in config['IMPORT_OBJECT_TYPES']:
                schemas = wrangler.wrangle_schema(db['DATABASE_NAME'], config['ENV_DATABASE_PREFIX'], config['ENV_ROLE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
        
            for schema in schemas:
                if schema['SCHEMA_NAME'] not in ['INFORMATION_SCHEMA']:  
                    tn2 = db['DATABASE_NAME'] + '.' + schema['SCHEMA_NAME'] + ' [schema]'
                    t2 = threading.Thread(target=task_schema, name=tn2, args=(semaphore, writer, sf, config, tn2, db['DATABASE_NAME'], db['DATABASE_NAME_SANS_ENV'], schema, current_role, available_roles, logger))
                    threads_list.append(t2)
                    #t2.start()
                    #t2.join()

            #####################################################
            # Stored Procs
            #ps = sf.procedures_get(database_name, schema['SCHEMA_NAME'], config['ENV_PROCEDURE_PREFIX'], config['ENV_DATABASE_PREFIX'], current_role, available_roles, ignore_roles_list)
            procs = []
            if not config['IMPORT_OBJECT_TYPES'] or 'PROCEDURE' in config['IMPORT_OBJECT_TYPES']:
                procs = wrangler.wrangle_procedure(db['DATABASE_NAME'], config['ENV_PROCEDURE_PREFIX'], config['ENV_DATABASE_PREFIX'], config['ENV_ROLE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            for p in procs:
                #tnp = database_name + '.' + schema['SCHEMA_NAME'] + '.' + p['PROCEDURE_NAME'] + p['PROCEDURE_SIGNATURE_TYPES'] + ' [sp]'
                tnp = db['DATABASE_NAME'] + '.' + p['SCHEMA_NAME'] + '.' + p['PROCEDURE_NAME'] + p['PROCEDURE_SIGNATURE_TYPES'] + ' [sp]'
                t3 = threading.Thread(target=task_procedure, name=tnp, args=(semaphore, writer, sf, config, tnp, db['DATABASE_NAME'], db['DATABASE_NAME_SANS_ENV'], p['SCHEMA_NAME'], p, logger))
                threads_list.append(t3)
                #t3.start()

            #####################################################
            # Functions
            #fs = sf.functions_get(database_name, schema['SCHEMA_NAME'], config['ENV_FUNCTION_PREFIX'], config['ENV_DATABASE_PREFIX'], current_role, available_roles, ignore_roles_list)
            funcs = []
            if not config['IMPORT_OBJECT_TYPES'] or 'FUNCTION' in config['IMPORT_OBJECT_TYPES']:
                funcs = wrangler.wrangle_function(db['DATABASE_NAME'], config['ENV_FUNCTION_PREFIX'], config['ENV_DATABASE_PREFIX'], config['ENV_ROLE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            for f in funcs:
                tnf = db['DATABASE_NAME'] + '.' + f['SCHEMA_NAME'] + '.' + f['FUNCTION_NAME'] + f['FUNCTION_SIGNATURE_TYPES'] + ' [func]'
                t4 = threading.Thread(target=task_function, name=tnf, args=(semaphore, writer, sf, config, tnf, db['DATABASE_NAME'], db['DATABASE_NAME_SANS_ENV'], f['SCHEMA_NAME'], f, logger))
                threads_list.append(t4)
                #t4.start()
                #t4.join()

            for t in threads_list:
                t.start()
            #for t in threads_list:
            #    t.join()
                
            #print(f'Thread {name} End')
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def task_schema(semaphore, writer, sf, config:dict, tn, database_name:str, database_name_sans_env:str, schema:dict, current_role:str, available_roles:list, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')

            writer.write_schema_file(database_name_sans_env, schema)

            threads_list = []

            #####################################################
            # Tags
            #tags = sf.tags_get(database_name, schema['SCHEMA_NAME'], current_role, available_roles, ignore_roles_list)
            tags = []
            if not config['IMPORT_OBJECT_TYPES'] or 'TAG' in config['IMPORT_OBJECT_TYPES']:
                tags = wrangler.wrangle_tag(database_name, schema['SCHEMA_NAME'], config['ENV_DATABASE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            for tag in tags:
                #print('^^^^^^^^^ BEFORE WRITE TAG FILE ^^^^^^^^^^')
                #print(tag)
                #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                writer.write_tag_file(database_name_sans_env, schema['SCHEMA_NAME'], tag)

            #####################################################
            # Objects (tables and views)
            #objects = sf.objects_get(database_name, schema['SCHEMA_NAME'], config['ENV_DATABASE_PREFIX'], current_role, available_roles, ignore_roles_list)
            objects = []
            if not config['IMPORT_OBJECT_TYPES'] or 'OBJECT' in config['IMPORT_OBJECT_TYPES']:
                objects = wrangler.wrangle_object(database_name, schema['SCHEMA_NAME'], config['ENV_DATABASE_PREFIX'], config['ENV_ROLE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            for obj in objects:
                tn2 = database_name + '.' + schema['SCHEMA_NAME'] + '.' + obj['OBJECT_NAME'] + ' [object]'
                t2 = threading.Thread(target=task_object, name=tn2, args=(semaphore, writer, sf, config, tn2, database_name, database_name_sans_env, schema['SCHEMA_NAME'], obj, logger))
                threads_list.append(t2)
                #t2.start()
                #t2.join()


            #####################################################
            # Tasks
            tasks = []
            if not config['IMPORT_OBJECT_TYPES'] or 'TASK' in config['IMPORT_OBJECT_TYPES']:
                tasks = wrangler.wrangle_task(database_name, schema['SCHEMA_NAME'], config['ENV_DATABASE_PREFIX'], config['ENV_ROLE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            for tsk in tasks:
                tntsk = database_name + '.' + schema['SCHEMA_NAME'] + '.' + tsk['TASK_NAME'] + ' [task]'
                t5 = threading.Thread(target=task_task, name=tntsk, args=(semaphore, writer, sf, config, tntsk, database_name, database_name_sans_env, schema['SCHEMA_NAME'], tsk, logger))
                threads_list.append(t5)
                #t5.start()
                #t5.join()

            #####################################################
            # Masking Policies
            masking_policies = []
            if not config['IMPORT_OBJECT_TYPES'] or 'MASKING POLICY' in config['IMPORT_OBJECT_TYPES']:
                masking_policies = wrangler.wrangle_masking_policy(database_name, schema['SCHEMA_NAME'], config['ENV_DATABASE_PREFIX'], config['ENV_ROLE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            for mpol in masking_policies:
                tnmp = database_name + '.' + schema['SCHEMA_NAME'] + '.' + mpol['MASKING_POLICY_NAME'] + ' [masking policy]'
                t6 = threading.Thread(target=task_masking_policy, name=tnmp, args=(semaphore, writer, sf, config, tnmp, database_name, database_name_sans_env, schema['SCHEMA_NAME'], mpol, logger))
                threads_list.append(t6)
                #t6.start()
                #t6.join()

            #####################################################
            # Row Access Policies
            row_access_policies = []
            if not config['IMPORT_OBJECT_TYPES'] or 'ROW ACCESS POLICY' in config['IMPORT_OBJECT_TYPES']:
                row_access_policies = wrangler.wrangle_row_access_policy(database_name, schema['SCHEMA_NAME'], config['ENV_DATABASE_PREFIX'], config['ENV_ROLE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            for rap in row_access_policies:
                tnrap = database_name + '.' + schema['SCHEMA_NAME'] + '.' + rap['ROW_ACCESS_POLICY_NAME'] + ' [row access policy]'
                t7 = threading.Thread(target=task_row_access_policy, name=tnrap, args=(semaphore, writer, sf, config, tnrap, database_name, database_name_sans_env, schema['SCHEMA_NAME'], rap, logger))
                threads_list.append(t7)
                #t7.start()
                #t7.join()

            for t in threads_list:
                t.start()
            #for t in threads_list:
            #    t.join()
                

            #print(f'Thread {name} End')
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def task_object(semaphore, writer, sf, config:dict, tn, database_name:str, database_name_sans_env:str, schema_name:str, obj:dict, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')
            #obj['COLUMNS'] = sf.columns_get(database_name, schema_name, obj['OBJECT_NAME'], config['ENV_DATABASE_PREFIX'])
            #obj['COLUMNS'] = wrangler.wrangle_column(database_name, schema_name, obj['OBJECT_NAME'], config['ENV_DATABASE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            writer.write_object_file(database_name_sans_env, schema_name, obj, config['OBJECT_METADATA_ONLY'], False)

            #print(f'Thread {name} End')
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def task_procedure(semaphore, writer, sf, config:dict, tn:str, database_name:str, database_name_sans_env:str, schema_name:str, p:dict, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')

            writer.write_procedure_file(database_name_sans_env, schema_name, p)

            #print(f'Thread {name} End')
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def task_function(semaphore, writer, sf, config:dict, tn:str, database_name:str, database_name_sans_env:str, schema_name:str, f:dict, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')

            writer.write_function_file(database_name_sans_env, schema_name, f)

            #print(f'Thread {name} End')
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def task_task(semaphore, writer, sf, config:dict, tn:str, database_name:str, database_name_sans_env:str, schema_name:str, tsk:dict, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')

            writer.write_task_file(database_name_sans_env, schema_name, tsk)

            #print(f'Thread {name} End')
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def task_masking_policy(semaphore, writer, sf, config:dict, tn:str, database_name:str, database_name_sans_env:str, schema_name:str, mp:dict, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')

            writer.write_masking_policy_file(database_name_sans_env, schema_name, mp)

            #print(f'Thread {name} End')
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)

def task_row_access_policy(semaphore, writer, sf, config:dict, tn:str, database_name:str, database_name_sans_env:str, schema_name:str, rap:dict, logger):
    #logger.log(threading.current_thread().name,'pre')
    with semaphore:
        thread_start_time = time.time()
        thread_name = threading.current_thread().name
        try:
            logger.log(thread_name,'Start')

            writer.write_row_access_policy_file(database_name_sans_env, schema_name, rap)

            #print(f'Thread {name} End')
            msg = 'created (%s seconds)' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
        except Exception as ex:
            traceback_text = traceback.format_exc() # get error traceback
            msg = 'error (%s seconds) - see error log at end' % (round(time.time() - thread_start_time,1))
            logger.log(thread_name,msg)
            logger.log_error(str(ex), thread_name, traceback_text)


def loop_logger(q:queue, keepRunning:bool, logger):
    thread_outputs = dict()

    while keepRunning:
        try:
            thread_name, msg = q.get_nowait()
            logger.log(thread_name,msg)
        except queue.Empty:
            # because the queue is used to update, there's no need to wait or block.
            pass

        #sys.stdout.write('\r' + pretty_output)
        #sys.stdout.flush()
        time.sleep(1)

def snowflake_import(args:dict):
    global logQueue
    start_time = time.time()

    logging.basicConfig(level=logging.ERROR)

    conf = configurator(args)
    config = conf.get_config()

    ###############################################################################################################
    #                                                   Logging
    ###############################################################################################################
    
    #logQueue = queue.Queue()
    #keepLoggerRunning = True
    logger = deploy_logger('info')
    #logger_thread = threading.Thread(target=loop_logger, name='logger_thread', args=(logQueue, keepLoggerRunning, logger))
    #logger_thread.start()
    
    ###############################################################################################################
    #                                                   Defaults
    ###############################################################################################################
    #deploy_db_name = '_DEPLOY'
    #excluded_databases = ['SNOWFLAKE_SAMPLE_DATA','SNOWFLAKE','SCHEMACHANGE']
    #max_threads = 3
    excluded_databases = config['EXCLUDED_DATABASES']
    #deploy_db_name = config['DEPLOY_DATABASE_NAME']
    import_databases = config['IMPORT_DATABASES']


    writer = yaml_writer()

    try:
        ###############################################################################################################
        #                                                   Connect to Snowflake
        ###############################################################################################################
        global wrangler 
        global available_roles
        global ignore_roles_list 

        logging.info('Connecting to Snowflake')
        sf = sf_client(config['SNOWFLAKE_PRIVATE_KEY'], config['SNOWFLAKE_PRIVATE_KEY_PASSWORD'], config['SNOWFLAKE_ACCOUNT'], config['SNOWFLAKE_USERNAME'], config['SNOWFLAKE_WAREHOUSE'], config['database'], config['schema'] )
        wrangler = wrangler(sf)
        #print('Connected to Snowflake')
        logging.info('Connected to Snowflake')

        # Get current role
        available_roles = []
        current_role = sf.current_role_get()
        available_roles.append(current_role)
        ignore_roles_list = config['STANDARD_ROLES']
        ignore_roles_list.append(current_role) # ignore out of the box roles PLUS the role that owns deployments (which can be hard coded in the files)
        
        #####################################################
        # Install Deploy DB if not exists
        is_installed = sf.deploy_db_check_installed(config['DEPLOY_DATABASE_NAME'])
        if not is_installed:
            sf.deploy_db_install(config['DEPLOY_DATABASE_NAME'])
            #print('Deploy DB Created')
            logging.info('Deploy DB Created')
        
        # Multithreading set up
        semaphore = threading.Semaphore(config['MAX_THREADS'])
        threads_role = []
        threads_wh = []
        threads_db = []

        logger.log('','Beginning to retrieve Snowflake metadata')

        #####################################################
        # INSTANCE START

        # Roles
        #rs = sf.roles_get(config['ENV_ROLE_PREFIX'], config['ENV_DATABASE_PREFIX'], current_role, available_roles, ignore_roles_list)
        rs = []
        if not config['IMPORT_OBJECT_TYPES'] or 'ROLE' in config['IMPORT_OBJECT_TYPES']:
            rs = wrangler.wrangle_role(config['ENV_ROLE_PREFIX'], config['ENV_DATABASE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            #print('import role')
            #print(rs)
        for r in rs:
            tnr = r['ROLE_NAME'] + ' [role]'
            t = threading.Thread(target=task_role, name=tnr, args=(semaphore, writer, sf, config, tnr, r, logger))
            threads_role.append(t)

        for t in threads_role:
            t.start()
        for t in threads_role:
            t.join()

        # Warehouses
        #whs = sf.warehouses_get(config['ENV_WAREHOUSE_PREFIX'], config['ENV_DATABASE_PREFIX'], current_role, available_roles, ignore_roles_list)
        whs = []
        if not config['IMPORT_OBJECT_TYPES'] or 'WAREHOUSE' in config['IMPORT_OBJECT_TYPES']:
            whs = wrangler.wrangle_warehouse(config['ENV_WAREHOUSE_PREFIX'], config['ENV_DATABASE_PREFIX'], config['ENV_ROLE_PREFIX'], config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'],semaphore)
            #print('import wh')
        for wh in whs:
            tnw = wh['WAREHOUSE_NAME'] + ' [warehouse]'
            t = threading.Thread(target=task_warehouse, name=tnw, args=(semaphore, writer, sf, config, tnw, wh, logger))
            threads_wh.append(t)
        
        for t in threads_wh:
            t.start()
        for t in threads_wh:
            t.join()
        #####################################################
        # DATA START
        
        # Databases
        #dbs = sf.databases_get(excluded_databases,config['DEPLOY_DATABASE_NAME'],config['ENV_DATABASE_PREFIX'], ignore_roles_list)
        dbs = []
        if not config['IMPORT_OBJECT_TYPES'] or 'DATABASE' in config['IMPORT_OBJECT_TYPES']:
            dbs = wrangler.wrangle_database(config['ENV_DATABASE_PREFIX'], config['ENV_ROLE_PREFIX'], excluded_databases, config['DEPLOY_DATABASE_NAME'], ignore_roles_list, config['DEPLOY_TAGS'],config['DEPLOY_ROLE'], available_roles, config['HANDLE_OWNERSHIP'], import_databases,semaphore)
        for db in dbs:
            if db['DATABASE_NAME'] not in excluded_databases:
                if import_databases == [] or db['DATABASE_NAME'] in import_databases:
                    tn =  db['DATABASE_NAME'] + ' [database]'
                    t = threading.Thread(target=task_db, name=tn, args=(semaphore, writer, sf, config, tn, db, current_role, available_roles, logger))
                    threads_db.append(t)

        for t in threads_db:
            t.start()
        for t in threads_db:
            t.join()
            
        # Masking Policies
        
        #####################################################
        # Thread management

        # Kick off all threads to begin execution
        #for t in threads:
        #    t.start()

        # if threads are not joined, the script will continue to run while the threads are also running.
        # Joining the threads means we will wait here until all the threads are done processing before continuing
        #for t in threads:
        #    t.join()

        # Wait till all threads have finished
        while len(threading.enumerate()) > 1:
            #print(len(threading.enumerate()))
            sleep(1)

        #keepLoggerRunning = False
        logger.log('','all objects have been pulled')
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
