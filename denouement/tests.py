from django.test import TestCase
from django.contrib.auth.models import Group, User


class SignUpViewTests(TestCase):

    # This gets called first
    def setUp(self):
        default_user_group = Group.objects.get_or_create(name='User')

    # Ensure the backend sees duplicate information and prompts user to change desired login credentials
    def test_denies_duplicate_username(self):
        sign_up_response = self.client.post('/account/signup/', 
            {'username': 'test', 'password': 'abcd123!', 'email': 'test@test.com'})
        
        duplicate_username_sign_up_response = self.client.post('/account/signup/', 
            {'username': 'test', 'password': 'test101@!', 'email': 'test123@test.com'})
        
        self.assertTemplateUsed(duplicate_username_sign_up_response, 'denouement/sign_up.html')

    # Ensure the backend denies identical usernames regardless of letter case and reprompts entry of desired credentials
    def test_denies_duplicate_username_case_insensitive(self):
        sign_up_response = self.client.post('/account/signup/', 
            {'username': 'test', 'password': 'abcd123!', 'email': 'test@test.com'})

        duplicate_username_case_insensitive_sign_up_response = self.client.post('/account/signup/', 
            {'username': 'tEsT', 'password': 'test101@!', 'email': 'test123@test.com'})

        self.assertTemplateUsed(duplicate_username_case_insensitive_sign_up_response, 'denouement/sign_up.html')
    
    # Ensure the backend sees duplicate information and prompts user to change desired login credentials
    def test_denies_duplicate_email(self):
        sign_up_response = self.client.post('/account/signup/', 
            {'username': 'test', 'password': 'abcd123!', 'email': 'abc@test.com'})

        duplicate_email_sign_up_response = self.client.post('/account/signup/', 
            {'username': 'test123', 'password': 'test101@!', 'email': 'abc@test.com'})

        self.assertTemplateUsed(duplicate_email_sign_up_response, 'denouement/sign_up.html')


class SignInViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test', password='test123!@')

    def test_username_case_insensitive(self):
        sign_in_response = self.client.post('/account/signin/',
            {'username': 'TeSt', 'password': 'test123!@'}, follow=True)

        self.assertTrue(sign_in_response.context['user'].is_authenticated)


