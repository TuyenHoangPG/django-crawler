import re
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

from .models import Property


class CrawlPropertySerializer(serializers.Serializer):
    number_of_property = serializers.IntegerField(required=True, min_value=0)

    __default_url = "https://batdongsan.com.vn/nha-dat-ban"
    __item_per_page = 20

    __options = Options()
    __options.add_argument("--no-sandbox")
    __options.add_argument("--disable-dev-shm-usage")
    __options.add_experimental_option("excludeSwitches", ["enable-automation"])
    __options.add_experimental_option("useAutomationExtension", False)

    def get_property(self, validated_data):
        try:
            number_of_property = validated_data.get("number_of_property")

            driver = webdriver.Chrome(options=self.__options)
            driver.get(self.__default_url)

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "product-lists-web"))
            )

            total_page = driver.find_elements(
                By.CSS_SELECTOR,
                ".re__pagination-group a.re__pagination-number",
            )[-1].get_attribute("pid")

            total_page = (
                int(total_page.replace(".", "")) if total_page is not None else 0
            )
            inserted_property = 0
            current_page = 1
            while inserted_property < number_of_property and current_page <= total_page:
                if current_page > 1:
                    driver.get(f"{self.__default_url}/p{current_page}")
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "product-lists-web"))
                    )

                list_all_property_container = driver.find_elements(
                    By.CSS_SELECTOR, f"#product-lists-web > .pr-container"
                )
                for property_container in list_all_property_container:
                    property = self.extract_property(property_container)
                    if property is not None:
                        property.save()
                        inserted_property = inserted_property + 1
                        if inserted_property >= number_of_property:
                            break

                current_page = current_page + 1

        except Exception as e:
            raise ValidationError(str(e.msg))

    def extract_property(self, property_element: WebElement):
        property = property_element.find_element(
            By.CSS_SELECTOR, "a.js__product-link-for-product-id"
        )
        property_id = property.get_attribute("data-product-id")

        if property_id is None:
            return None

        existed_property = Property.objects.filter(property_id=property_id)
        if existed_property.exists():
            return None

        property_entity = Property()
        property_entity.property_id = property_id
        property_entity.url = self.__default_url + str(property.get_attribute("href"))

        property_detail_driver = webdriver.Chrome(options=self.__options)
        property_detail_driver.get(property_entity.url)

        WebDriverWait(property_detail_driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "re__pr-description"))
        )

        property_detail = property_detail_driver.find_element(
            By.ID, "product-detail-web"
        )
        property_entity.title = property_detail.find_element(
            By.CLASS_NAME, "pr-title"
        ).text
        property_entity.address = property_detail.find_element(
            By.CLASS_NAME, "re__pr-short-description"
        ).text
        property_entity.images = [
            url.get_attribute("src")
            for url in property_detail.find_elements(
                By.CSS_SELECTOR,
                ".re__media-thumbs .re__media-thumb-item img",
            )
        ]
        property_entity.description = property_detail.find_element(
            By.CLASS_NAME, "re__detail-content"
        ).text

        attributes = property_detail.find_elements(
            By.CLASS_NAME, "re__pr-specs-content-item"
        )
        for attr in attributes:
            title = attr.find_element(
                By.CLASS_NAME, "re__pr-specs-content-item-title"
            ).text
            value = attr.find_element(
                By.CLASS_NAME, "re__pr-specs-content-item-value"
            ).text

            self.normalize_property_attribute(property_entity, title, value)

        property_detail_driver.close()

        return property_entity

    def normalize_property_attribute(self, property: Property, title: str, value: str):
        pattern = r"\d+(\.)?\d*"
        if title == "Diện tích":
            match = re.search(pattern, value)
            if match:
                property.area = float(match.group(0))
        elif title == "Mức giá":
            match = re.search(pattern, value)
            if match:
                property.price = float(match.group(0))
        elif title == "Nội thất":
            property.furniture = value
        elif title == "Số phòng ngủ":
            bedroom_pattern = r"\d+"
            match = re.search(bedroom_pattern, value)
            if match:
                property.bedrooms = float(match.group(0))


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = "__all__"
