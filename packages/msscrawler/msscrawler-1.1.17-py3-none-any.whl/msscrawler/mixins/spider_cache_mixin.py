class SpiderCacheMixin:

    def __init__(self):
        self.cache_spider = []  # [{'name': '', count: 0} ]

    def choose_spider(self, spider_name):
        found_spider = None
        found_index = 0
        for i, spider in enumerate(self.cache_spider):
            if spider["name"] == spider_name:
                found_spider = spider
                found_index = i

        if found_spider:
            # check another spider in cache_spider has minimum count
            count_array = map(lambda x: x["count"], self.cache_spider)

            min_count = min(count_array)

            # print("min_count", min_count)

            # compare count with found_spider count
            has_choose = found_spider["has_choose"]

            # set not choose to all
            for i, spider in enumerate(self.cache_spider):
                self.cache_spider[i]["has_choose"] = False

            if found_spider["count"] > min_count and has_choose:
                return False

            # choose => set has_choose = True
            self.cache_spider[found_index]["has_choose"] = True

        else:
            # spider not in cache => set all count to 0
            for i, spider in enumerate(self.cache_spider):
                self.cache_spider[i]["count"] = 0
                self.cache_spider[i]["has_choose"] = False

            self.cache_spider.append({"name": spider_name, "count": 0, "has_choose": True})

        return True

    def increase_spider_count(self, spider_name):
        for i, spider in enumerate(self.cache_spider):
            if spider["name"] == spider_name:
                self.cache_spider[i] = {
                    "name": spider_name,
                    "count": spider["count"] + 1,
                    "has_choose": spider["has_choose"],
                }