Feature: Use SimpleDB as a data provider
  In order to use SimpleDB as a data provider
  As a worker
  I want to access domains and process data
  
  Scenario: Get a SimpleDB domain name for a particular environment
    Given I have imported a settings module
    And I have the settings environment <env>
    And I get the settings
    And I have a setting for <postfix>
    And I get a setting for postfix <postfix>
    And I have imported the SimpleDB provider module
    When I get the domain name from the SimpleDB provider for <domain>
    Then I have a domain name equal to the domain plus the postfix

  Examples:
    | env    | postfix                 | domain
    | dev    | simpledb_domain_postfix | S3File
    | dev    | simpledb_domain_postfix | S3FileLog
    | live   | simpledb_domain_postfix | S3File
    | live   | simpledb_domain_postfix | S3FileLog
    
  Scenario: Build SimpleDB queries for elife articles bucket
    Given I have imported the SimpleDB provider module
    And I have the domain name S3FileLog_dev
    And I have the file data types ["xml", "pdf", "img", "suppl", "video"]
    And I have the date format %Y-%m-%dT%H:%M:%S.000Z
    And I have the bucket name elife-articles
    And I have the file data type <file_data_type>
    And I have the doi id <doi_id>
    And I have the last updated since <last_updated_since>
    When I get the query from the SimpleDB provider
    Then I have the SimpleDB query <query>
  
  Examples:
    | file_data_type | doi_id | last_updated_since       | query
    | None           | None   | None                     | select * from S3FileLog_dev where bucket_name = 'elife-articles' and name is not null order by name asc
    | xml            | None   | None                     | select * from S3FileLog_dev where bucket_name = 'elife-articles' and name like '%.xml%' order by name asc
    | None           | 00013  | None                     | select * from S3FileLog_dev where bucket_name = 'elife-articles' and name like '00013/%' order by name asc
    | None           | None   | 2013-01-01T00:00:00.000Z | select * from S3FileLog_dev where bucket_name = 'elife-articles' and last_modified_timestamp > '1356998400' and name is not null order by name asc
    | xml            | 00013  | None                     | select * from S3FileLog_dev where bucket_name = 'elife-articles' and name like '%.xml%' and name like '00013/%' order by name asc
    | None           | 00013  | 2013-01-01T00:00:00.000Z | select * from S3FileLog_dev where bucket_name = 'elife-articles' and name like '00013/%' and last_modified_timestamp > '1356998400' order by name asc
    | xml            | None   | 2013-01-01T00:00:00.000Z | select * from S3FileLog_dev where bucket_name = 'elife-articles' and name like '%.xml%' and last_modified_timestamp > '1356998400' order by name asc
    | xml            | 00013  | 2013-01-01T00:00:00.000Z | select * from S3FileLog_dev where bucket_name = 'elife-articles' and name like '%.xml%' and name like '00013/%' and last_modified_timestamp > '1356998400' order by name asc
    
  Scenario: Get the latest S3 files from SimpleDB provider and count results
    Given I have imported the SimpleDB provider module
    And I have the file data types ["xml", "pdf", "img", "suppl", "video"]
    And I have a document <document>
		And I get JSON from the document
		And I parse the JSON string
    When I get the latest article S3 files from SimpleDB
    Then I have an item list count <count>

  Examples:
    | document                                                  | count
    | test_data/provider.simpleDB.elife_articles.latest01.json  | 19   
    | test_data/provider.simpleDB.elife_articles.latest02.json  | 4     
    
  Scenario: Get the latest S3 files from SimpleDB provider and check values
    Given I have imported the SimpleDB provider module
    And I have the file data types ["xml", "pdf", "img", "suppl", "video"]
    And I have a document <document>
		And I get JSON from the document
		And I parse the JSON string
    When I get the latest article S3 files from SimpleDB
    Then the item list <index> <key> is <value>
    
  Examples:
    | document                                                  | index | key                     | value
    | test_data/provider.simpleDB.elife_articles.latest01.json  | 9     | name                    | 00005/elife_2012_00005.video.zip
    | test_data/provider.simpleDB.elife_articles.latest01.json  | 3     | name                    | 00003/elife_2012_00003.xml.zip
    | test_data/provider.simpleDB.elife_articles.latest01.json  | 7     | name                    | 00005/elife_2012_00005.pdf.zip
    | test_data/provider.simpleDB.elife_articles.latest01.json  | 7     | last_modified_timestamp | 1359244876
    | test_data/provider.simpleDB.elife_articles.latest02.json  | 0     | name                    | 00003/elife_2012_00003.xml.zip
    | test_data/provider.simpleDB.elife_articles.latest02.json  | 3     | name                    | 00048/elife_2012_00048.xml.r6.zip
    | test_data/provider.simpleDB.elife_articles.latest02.json  | 1     | name                    | 00005/elife00005.xml
    | test_data/provider.simpleDB.elife_articles.latest02.json  | 1     | last_modified_timestamp | 1359244983
    
    