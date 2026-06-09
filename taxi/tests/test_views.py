from django.test import TestCase
from django.urls import reverse

from taxi.models import Driver, Manufacturer, Car


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.driver = Driver.objects.create_user(
            username="UsernameTest",
            password="DriverPassword",
            first_name="DriverFirstName",
            last_name="DriverLastName",
            license_number="ADM12345",
        )
        cls.manufacturer_first = Manufacturer.objects.create(
            name="Toyota",
            country="Japan",
        )
        cls.manufacturer_second = Manufacturer.objects.create(
            name="Volkswagen",
            country="Germany",
        )

    def test_anonymous_user_redirect_to_login(self):
        response = self.client.get(reverse("taxi:car-list"))
        self.assertEqual(response.status_code, 302)

    def test_index_page(self):
        self.client.force_login(self.driver)
        response = self.client.get(reverse("taxi:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["num_visits"], 1)
        response = self.client.get(reverse("taxi:index"))
        self.assertEqual(response.context["num_visits"], 2)

    def test_custom_search(self):
        self.client.force_login(self.driver)
        response = self.client.get(
            reverse("taxi:manufacturer-list"),
            data={"name": "Toyota"}
        )
        self.assertIn(
            self.manufacturer_first,
            response.context["manufacturer_list"]
        )
        self.assertNotIn(
            self.manufacturer_second,
            response.context["manufacturer_list"]
        )

    def test_toggle_assign_to_car(self):
        car = Car.objects.create(
            model="Supra",
            manufacturer=self.manufacturer_first,
        )
        self.client.force_login(self.driver)
        response = self.client.get(
            reverse("taxi:toggle-car-assign", args=[car.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(car, self.driver.cars.all())
