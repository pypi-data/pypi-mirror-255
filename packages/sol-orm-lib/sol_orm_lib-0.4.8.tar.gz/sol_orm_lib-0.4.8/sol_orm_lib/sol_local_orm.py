import sys
import time

import mysql.connector
from loguru import logger

from .models import *

logger.remove()
logger.add(sys.stdout, colorize=True, 
           format="<le>[{time:DD-MM-YYYY HH:mm:ss}]</le> <lvl>[{level}]: {message}</lvl>", 
           level="INFO")


class SolLocalORM:
    
    def __init__(self, host, port, db, user, password, debug=False):
        """
        Initializes the instance with a connection to the MySQL database.

        Args:
            host (str): The host name or IP address of the MySQL server.
            port (int): The port number where the MySQL server is listening.
            db (str): The name of the database to connect to.
            user (str): The username to authenticate with the MySQL server.
            password (str): The password to authenticate with the MySQL server.
            debug (bool, optional): If True, the logger is set to output to stdout with DEBUG level. 
                                    Defaults to False.

        """
        self.db = MySQLClient(
            host=host,
            port=port,
            db=db,
            user=user,
            password=password
        )
        
        if debug:
            logger.remove()
            logger.add(sys.stdout, colorize=True, 
                    format="<le>[{time:DD-MM-YYYY HH:mm:ss}]</le> <lvl>[{level}]: {message}</lvl>", 
                    level="DEBUG")
    
    # =========================================================================== #
    # Public Methods
    # =========================================================================== #
    def add_entity(self, entity):
        match entity.__class__.__name__:
            case "OutputPVMeasuredTAC":
                self._add_output_pv_measured_tac(entity)
            case "ProgramOptLowTAC":
                self._add_program_opt_low_tac(entity)
            case "StorageStatusTAC":
                self._add_storage_status_tac(entity)
            case "SOLLog":
                self._add_sol_log(entity)
            case _:
                logger.error(f"Entity add for {entity.__class__.__name__} not supported")
        
    def get_entity(self, entity_class, id, id2=None):
        match entity_class.__name__:
            case "OutputPVMeasuredTAC":
                return self._get_output_pv_measured_tac(id, id2)
            case "StorageStatusTAC":
                return self._get_storage_status_tac(id, id2)
            case "OptimizationParameter":
                return self._get_optimization_parameter(id)
            case "SpotPublishedTIC":
                return self._get_spot_published_tic(id)
            case "TIC":
                return self._get_tic(id)
            case "SOLLog":
                return self._get_sol_log(id)
            case _:
                logger.error(f"Get entity for {entity_class.__name__} not supported")
                
    def get_last_entity(self, entity_class):
        match entity_class.__name__:
            case "OutputPVMeasuredTAC":
                return self._get_last_output_pv_measured_tac()
            case "StorageStatusTAC":
                return self._get_last_storage_status_tac()
            case "SpotPublishedTIC":
                return self._get_last_spot_published_tic()
            case "TIC":
                return self._get_last_tic()
            case "SOLLog":
                return self._get_last_sol_log()
            case _:
                logger.error(f"Get last entity for {entity_class.__name__} not supported")        
    
    # =========================================================================== #
    # ADD Methods
    # =========================================================================== #        
    def _add_output_pv_measured_tac(self, entity):
        statement = f"""
            INSERT INTO OutputPVMeasuredTACs (
                k,
                n,
                outputPVKwh
            ) VALUES (
                {entity.k},
                {entity.n},
                {entity.outputPVKwh}
            )
            """
        success = self.db.insert(statement)
        if success:
            logger.success(f"Entity {entity} inserted successfully in local database")
        else:
            logger.error(f"Failed to insert entity {entity}")
        
    def _add_program_opt_low_tac(self, entity):
        statement = f"""
            INSERT INTO ProgramOptLowTACs (
                k,
                n,
                pvInvSent,
                storageInvSent
            ) VALUES (
                {entity.k},
                {entity.n},
                {entity.pvInvSent},
                {entity.storageInvSent}
            )
            """
        success = self.db.insert(statement)
        if success:
            logger.success(f"Entity {entity} inserted successfully in local database")
        else:
            logger.error(f"Failed to insert entity {entity}")
            
    def _add_storage_status_tac(self, entity):
        statement = f"""
            INSERT INTO StorageStatusTACs (
                k,
                n,
                storageActual,
                storageInverterRealised,
                storageActualKwh,
                storageMax
            ) VALUES (
                {entity.k},
                {entity.n},
                {entity.storageActual},
                {entity.storageInverterRealised},
                {entity.storageActualKwh},
                {entity.storageMax}
            )
            """
        success = self.db.insert(statement)
        if success:
            logger.success(f"Entity {entity} inserted successfully in local database")
        else:
            logger.error(f"Failed to insert entity {entity}")
            
    def _add_sol_log(self, entity):
        statement = f"""
            INSERT INTO SOLLogs (
                source,
                message,
                details,
                type
            ) VALUES (
                '{entity.source}',
                '{entity.message}',
                '{entity.details}',
                '{entity.type}'
            )
            """
        success = self.db.insert(statement)
        if success:
            logger.success(f"Entity {entity} inserted successfully in local database")
        else:
            logger.error(f"Failed to insert entity {entity}")

    # =========================================================================== #
    # GET Methods
    # =========================================================================== # 
    def _get_output_pv_measured_tac(self, k: int , n: int) -> OutputPVMeasuredTAC:
        statement = f"""
            SELECT *
            FROM OutputPVMeasuredTACs
            WHERE k = {k}
            AND n = {n}
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity OutputPVMeasuredTAC with k={k} and n={n} not found")
        else:
            logger.debug(result)
            return OutputPVMeasuredTAC(
                k=result[0],
                n=result[1],
                outputPVKwh=result[2]
            )
        
    def _get_storage_status_tac(self, k: int, n: int) -> StorageStatusTAC:
        statement = f"""
            SELECT *
            FROM StorageStatusTACs
            WHERE k = {k}
            AND n = {n}
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity StorageStatusTAC with k={k} and n={n} not found")
        else:
            logger.debug(result)
            return StorageStatusTAC(
                k=result[0],
                n=result[1],
                storageActual=result[2],
                storageInverterRealised=result[3],
                storageActualKwh=result[4],
                storageMax=result[5]
            )
        
    def _get_optimization_parameter(self, name: str) -> OptimizationParameter:
        statement = f"""
            SELECT *
            FROM OptimizationParameters
            WHERE name = {name}
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity OptimizationParameter with name={name}")
        else:
            logger.debug(result)
            return OptimizationParameter(
                name=result[0],
                value=result[1],
                unit=result[2]
            )
        
    def _get_spot_published_tic(self, k: int) -> SpotPublishedTIC:
        statement = f"""
            SELECT *
            FROM SpotPublishedTICs
            WHERE k = {k}
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity SpotPublishedTIC with k={k} not found")
        else:
            logger.debug(result)
            return SpotPublishedTIC(
                k=result[0],
                spotMwhEUR=result[1],
                acceptedProgramKwh=result[2],
                publishK=result[3]
            )
        
    def _get_tic(self, k: int) -> TIC:
        statement = f"""
            SELECT *
            FROM TICs
            WHERE k = {k}
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity TIC with k={k} not found")
        else:
            logger.debug(result)
            return TIC(
                k=result[0],
                timestamp=result[1],
                pvPlannedDown=result[2],
                stgPlannedDown=result[3],
                allPlannedDown=result[4]
            )      
        
    def _get_sol_log(self, id: int) -> SOLLog:
        statement = f"""
            SELECT *
            FROM SOLLogs
            WHERE id = {id}
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity SOLLog with id={id} not found")
        else:
            logger.debug(result)
            return SOLLog(
                id=result[0],
                source=result[1],
                message=result[2],
                details=result[3],
                type=result[4],
                timestamp=result[5]
            )          

    # =========================================================================== #
    # GET LAST Methods
    # =========================================================================== # 
    def _get_last_output_pv_measured_tac(self) -> OutputPVMeasuredTAC:
        statement = f"""
            SELECT *
            FROM (
                SELECT *
                FROM OutputPVMeasuredTACs
                ORDER BY k DESC
                LIMIT 1
            ) AS LastK
            ORDER BY n DESC
            LIMIT 1
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity OutputPVMeasuredTAC not found")
        else:
            logger.debug(result)
            return OutputPVMeasuredTAC(
                k=result[0],
                n=result[1],
                outputPVKwh=result[2]
            )
        
    def _get_last_storage_status_tac(self) -> StorageStatusTAC:
        statement = f"""
            SELECT *
            FROM (
                SELECT *
                FROM StorageStatusTACs
                ORDER BY k DESC
                LIMIT 1
            ) AS LastK
            ORDER BY n DESC
            LIMIT 1
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity StorageStatusTAC not found")
        else:
            logger.debug(result)
            return StorageStatusTAC(
                k=result[0],
                n=result[1],
                storageActual=result[2],
                storageInverterRealised=result[3],
                storageActualKwh=result[4],
                storageMax=result[5]
            )
        
    def _get_last_spot_published_tic(self) -> SpotPublishedTIC:
        statement = f"""
            SELECT *
            FROM SpotPublishedTICs
            ORDER BY k DESC
            LIMIT 1
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity SpotPublishedTIC not found")
        else:
            logger.debug(result)
            return SpotPublishedTIC(
                k=result[0],
                spotMwhEUR=result[1],
                acceptedProgramKwh=result[2],
                publishK=result[3]
            )
        
    def _get_last_tic(self) -> TIC:
        statement = f"""
            SELECT *
            FROM TICs
            ORDER BY k DESC
            LIMIT 1
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity TIC not found")
        else:
            logger.debug(result)
            return TIC(
                k=result[0],
                timestamp=result[1],
                pvPlannedDown=result[2],
                stgPlannedDown=result[3],
                allPlannedDown=result[4]
            )   
        
    def _get_last_sol_log(self) -> SOLLog:
        statement = f"""
            SELECT *
            FROM SOLLogs
            ORDER BY id DESC
            LIMIT 1
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity SOLLog not found")
        else:
            logger.debug(result)
            return SOLLog(
                id=result[0],
                source=result[1],
                message=result[2],
                details=result[3],
                type=result[4],
                timestamp=result[5]
            )          
      
    # =========================================================================== #
    # Legacy functions
    # =========================================================================== #
    def insert_total_power_today_kwh(self, timestamp, total_power):
        statement = f"""
            INSERT INTO total_power_today (
                timestamp,
                total_power_today
            ) VALUES (
                {timestamp},
                {total_power}
            )
            """
        success = self.db.insert(statement)
        if success:
            logger.success(f"'total_power_today' inserted successfully in local database")
        else:
            logger.error(f"Failed to insert 'total_power_today'")
        
    def get_total_power_today_kwh(self):
        statement = f"""
            SELECT total_power_today
            FROM total_power_today
            ORDER BY timestamp DESC
            LIMIT 1
            """
        result = self.db.select(statement)
        if result is None:
            logger.error(f"Entity total_power_today not found")
        else:
            return result[0]



class MySQLClient:
    
    cnx = None
    
    def __init__(self, **kwargs):
        """Establish connection to database"""
        while True:
            try:
                self.cnx = self._get_db_connection(kwargs)
                if self.cnx is None:
                    logger.info("Will try to reconnect in 10 seconds")
                    time.sleep(5)
                    continue
                else:
                    break
            except Exception as e:
                logger.error(f"An unexpected error ocurred establishing connection with the database: {e}")
                
    def _get_db_connection(self, kwargs) -> mysql.connector:
        """
        Establishes a connection to the MySQL database using credentials from the 
        settings module.

        Returns:
            Connection: The Connection object for the database if successful. 
                        Returns None if a connection could not be established.
        Raises:
            mysql.connector.Error: If a connection to the database could not be 
                                established.
        """
        logger.info("Trying to connect to MySQL...")
        cnx = None

        try:
            cnx = mysql.connector.connect(
                host=kwargs["host"],
                user=kwargs["user"],
                password=kwargs["password"],
                database=kwargs["db"],
                autocommit=True  # This can help with preventing hanging transactions
            )
            logger.success("Connection established")
        except mysql.connector.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            
        return cnx
        
    def insert(self, statement: str) -> bool:
        """
        Executes an SQL INSERT statement on the database.

        Args:
            statement (str): The SQL INSERT statement to be executed.
        Returns:
            bool: True if the statement was executed successfully, False otherwise.
        Raises:
            mysql.connector.Error: If there is an error executing the SQL statement.
        """
        cursor = self.cnx.cursor()
        try:
            cursor.execute(statement)
            return True
        except mysql.connector.Error as e:
            logger.error(f"Failed to insert entity: {e}")
            return False
        finally:
            cursor.close()
            
    def select(self, statement: str) -> tuple:
        """
        Executes an SQL SELECT statement on the database and fetches the first row of the result.

        Args:
            statement (str): The SQL SELECT statement to be executed.
        Returns:
            tuple: The first row of the result set. None if the query fails or if there are no results.
        Raises:
            mysql.connector.Error: If there is an error executing the SQL statement.
        """
        cursor = self.cnx.cursor()
        try:
            cursor.execute(statement)
            result = cursor.fetchone()
            return result
        except mysql.connector.Error as e:
            logger.error(f"Failed to retrieve entity: {e}")
            return None
        finally:
            cursor.close()
