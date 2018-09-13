from django.test import TestCase
from django.contrib.auth.models import Group

class SignUpViewTests(TestCase):

    # This gets called first
    def setUp(self):
        default_user_group = Group.objects.get_or_create(name='User')

    # Ensure the backend sees duplicate information and prompts user to change desired login credentials
    def test_denies_duplicate_username(self):
        sign_up_response = self.client.post('/account/signup/', {'username': 'test', 'password': 'abcd123!', 'email': 'test@test.com'})
        duplicate_username_sign_up_response = self.client.post('/account/signup/', 
            {'username': 'test', 'password': 'test101@!', 'email': 'test123@test.com'})
        self.assertTemplateUsed(duplicate_username_sign_up_response, 'denouement/sign_up.html')

    def test_denies_duplicate_email(self):
        sign_up_response = self.client.post('/account/signup/', {'username': 'test', 'password': 'abcd123!', 'email': 'abc@test.com'})
        duplicate_email_sign_up_response = self.client.post('/account/signup/', 
            {'username': 'test', 'password': 'test101@!', 'email': 'abc@test.com'})
        self.assertTemplateUsed(duplicate_email_sign_up_response, 'denouement/sign_up.html')


