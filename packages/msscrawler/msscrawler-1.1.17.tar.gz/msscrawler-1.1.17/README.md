# Common package for crawler project
This package contains base classes to implement site-specific crawlers. 
It aims to help implementation of specific crawlers easier with plugging what you need into 
a stable and unified crawling structure

## Class Structure
### DatabaseMixin
> crawler.mixins.database_mixin.DatabaseMixin
> 
This class provides database-related interface/mixin for its child to extend

Summary of class implementation:
> init constructor:
> 
>   - init parent class
>   
>   - setup_database
> 
>     - load database env vars from os
> 
>     - init database connector (this method instantiates a concrete DB connector extends 
>     from BaseDatabaseConnector. Ex: MongoDBConnector )

> other database-related methods:
>
>   - make call to self.database_client (instance of class derived from BaseDatabaseConnector) 
> for db works

### MessageConnectorMixin
> crawler.mixins.message_connector_mixin.MessageConnectorMixin
> 

This class provides message-related interface/mixin for its child to extend

Summary of class implementation:
> init constructor:
> 
>   - init parent class
>   
>   - setup_connector
> 
>     - load message broker env vars from os
> 
>     - init message broker connector (this method instantiates a concrete Message connector extends 
>     from BaseMessageBrokerConnector. Ex: RabbitMQConnector )

> other message-related methods:
>
>   - make call to connector's methods (instance of class derived from BaseMessageBrokerConnector) 
> to send and receive messages

### BaseDatabaseConnector
> crawler.connectors.databases.base.BaseDatabaseConnector

This base class provides interface/mixin for a database-related connector.
Instances of this class should be used as a member of a Crawler/Pipline to make calls to database

### BaseMessageBrokerConnector
> crawler.connectors.message_brokers.base.BaseMessageBrokerConnector

This base class provides interface/mixin for a message-related connector.
Instances of this class should be used as a member of a Crawler/Pipline to send/receive messages

### BaseItem
> crawler.items.base.BaseItem

This base class (extends scrapy.Item) contains base properties for an item. 
Extends this class for mode detailed item.

### BasePipeline
> crawler.pipelines.base.BasePipeline

This base class (extends DatabaseMixin, MessageConnectorMixin) provides database-related 
and message-related interface/mixin for a scrapy pipeline.

### BaseCrawler
> crawler.base_crawler.BaseCrawler

This base class (extends DatabaseMixin, MessageConnectorMixin) provides database-related 
and message-related interface/mixin for a Crawler 
(Ex: Crawler for shopping site main page/category page/product page)

Call ```crawler.run()``` from subclass's instance should load all env vars 
and start all steps of a crawling job

Example:
```
site = WebsiteCrawler()
site.run()
```

### BaseSpider
> crawler.spiders.base.BaseSpider

This base class extends ```spiders.Spider```

The inherited ```def parse(self, response, **kwargs):``` method from ```spiders.Spider``` 
is implemented with following steps:
> - an ```items``` object will be created with default value (set_default_value), this ```items``` is yielded to pipeline
> - get_css_selector
> - loop through all item returned by css_selector
>   - process returned item, reimplement to check is_element_valid if item need to be filtered again 
> - process response and a list contains filtered item again using ```process_response```, return final ```items``` object
> - yield ```items``` to pipeline 

Methods should be inherited/overriden when implementing new spider:

```def is_element_valid(self, element):``` : filter the response's element again to confirm it is a valid element

```def process_response(self, response, items, response_elements):``` : final work before yielding an object t pipeline

```def get_new_item_instance():``` : get new instance from subclass of ```BaseItem```

```def set_default_value(self):``` : set default value of item

```def get_css_selector(self):``` : css selector to get html element(s) from response

### Run demo theamall.com implementation
```
import os

from dotenv import load_dotenv

from crawler.sites.shopping.website_crawler import WebsiteCrawler

if __name__ == '__main__':
    load_dotenv(os.path.abspath('.env-base'))
    site = WebsiteCrawler()
    site.run()
```