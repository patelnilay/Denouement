from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist


class SignUpViewTests(TestCase):

    # This gets called first
    def setUp(self):
        default_user_group = Group.objects.get_or_create(name='User')

    # Duplication tests ------------------------------------------------------------
    def test_denies_duplicate_username(self):
        sign_up_response = self.client.post('/account/signup/', 
            {'username': 'test', 'password': 'abcd123!', 'email': 'test@test.com'})
        
        duplicate_username_sign_up_response = self.client.post('forums/account/signup/', 
            {'username': 'test', 'password': 'test101@!', 'email': 'test123@test.com'})
        
        self.assertRaises(ObjectDoesNotExist, User.objects.get, email='test123@test.com')

    def test_denies_duplicate_username_case_insensitive(self):
        sign_up_response = self.client.post('/forums/account/signup/', 
            {'username': 'test', 'password': 'abcd123!', 'email': 'test@test.com'})

        duplicate_username_case_insensitive_sign_up_response = self.client.post('/account/signup/', 
            {'username': 'tEsT', 'password': 'test101@!', 'email': 'test123@test.com'})

        self.assertRaises(ObjectDoesNotExist, User.objects.get, email='test123@test.com')

    def test_denies_duplicate_email(self):
        sign_up_response = self.client.post('/forums/account/signup/', 
            {'username': 'test', 'password': 'abcd123!', 'email': 'abc@test.com'})

        duplicate_email_sign_up_response = self.client.post('/forums/account/signup/', 
            {'username': 'test123', 'password': 'test101@!', 'email': 'abc@test.com'})
    
        self.assertRaises(ObjectDoesNotExist, User.objects.get, username='test123')
    # ------------------------------------------------------------------------------


class SignInViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test', password='test123!@')

    def test_username_case_insensitive(self):
        sign_in_response = self.client.post('/forums/account/signin/',
            {'username': 'TeSt', 'password': 'test123!@'}, follow=True)

        self.assertTrue(sign_in_response.context['user'].is_authenticated)


class ViewUserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test123!@')
        self.client.force_login(self.user)

    # When a user views their own profile it should redirect them to their
    # account management page
    def test_account_redirect(self):
        view_profile_response = self.client.get('/forums/user/' + self.user.username, follow=False)
        self.assertRedirects(view_profile_response, '/forums/account/')



