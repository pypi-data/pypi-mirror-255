import logging
import unittest
from tests.snippet.files import Test_with_files
from chibi import config
from chibi.atlas import Chibi_atlas
from chibi.config.config import Logger
from chibi.config import Configuration


class Test_load_config( Test_with_files ):
    def test_should_load_the_settings_from_a_pyton_file( self ):
        python_file = self.root_dir.temp_file( extension='py' )
        self.assertNotIn( 'hello', config.configuration  )
        with python_file as f:
            f.append( 'from chibi.config import configuration\n' )
            f.append( 'configuration.hello = "asdf"' )

        config.load( python_file )
        self.assertEqual( config.configuration.hello, 'asdf' )

    def test_when_read_a_json_should_put_all_the_content_in_the_config( self ):
        json_file = self.root_dir.temp_file( extension='json' )
        self.assertNotIn( 'json_hello', config.configuration  )
        with json_file as f:
            f.write( { 'json_hello': '1234567890' } )

        config.load( json_file )
        self.assertEqual( config.configuration.json_hello, '1234567890' )

    def test_when_read_a_yaml_should_put_all_the_content_in_the_config( self ):
        yaml_file = self.root_dir.temp_file( extension='yaml' )
        self.assertNotIn( 'yaml_hello', config.configuration  )
        with yaml_file as f:
            f.write( { 'yaml_hello': 'qwertyuiop' } )

        config.load( yaml_file )
        self.assertEqual( config.configuration.yaml_hello, 'qwertyuiop' )


class Test_config_default_factory( unittest.TestCase ):
    def setUp( self ):
        super().setUp()
        self.config = Configuration()

    def test_should_create_chibi_atlas_by_default( self ):
        self.assertNotIn( 'new_config', self.config )
        result = self.config.new_config
        self.assertIsInstance( result, Chibi_atlas )


class Test_logger( unittest.TestCase ):
    def setUp( self ):
        super().setUp()
        from chibi.config import configuration
        self.config = configuration
        self.logger = logging.getLogger( 'test.config' )

    def test_should_return_a_instance_of_logger( self ):
        logger = self.config.loggers[ 'test.config' ]
        self.assertIsInstance( logger, Logger )

    def test_should_return_the_current_level( self ):
        logger = self.config.loggers[ 'test.config' ]
        self.assertEqual( logger.level, self.logger.parent.level )

    def test_when_is_set_the_level( self ):
        logger = self.config.loggers[ 'test.config' ]
        current_level = self.logger.level
        logger.level = logging.INFO
        self.assertEqual( logger.level, self.logger.level )
        logger.level = current_level


class Test_envars( unittest.TestCase ):
    def setUp( self ):
        super().setUp()
        from chibi.config import configuration
        self.config = configuration

    def test_envars_should_no_be_empty( self ):
        self.assertTrue( self.config.env_vars )
