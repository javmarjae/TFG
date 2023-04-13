from django.test import TestCase, Client
from django.urls import reverse
from .models import Friendship, Gamer, User, Report, Clan, Gameship
from .forms import ReportCreateForm
from chat.models import Thread
from datetime import datetime
from django.utils import timezone
from django.contrib.messages import get_messages

# FriendsView

class FriendsViewTest(TestCase):
    
    def test_accept_friendship(self):
        user1 = User.objects.create_user('user1', password='pass123')
        user2 = User.objects.create_user('user2', password='pass123')
        gamer1 = Gamer.objects.create(user=user1)
        gamer2 = Gamer.objects.create(user=user2)
        
        friendship = Friendship.objects.create(sender=gamer1, receiver=gamer2, status='pe')
        
        self.client.login(username='user2', password='pass123')
        response = self.client.post(reverse('friends'), data={'accept': '1', 'solicitud': friendship.id})
        
        friendship.refresh_from_db()
        self.assertEqual(friendship.status, 'ac')
        
        thread_exists = Thread.objects.filter(first_person=friendship.sender.user, second_person=friendship.receiver.user).exists()
        self.assertTrue(thread_exists)
        
        self.assertTemplateUsed(response, 'friends.html')

    def test_decline_friendship(self):
        user1 = User.objects.create_user('user1', password='pass123')
        user2 = User.objects.create_user('user2', password='pass123')
        gamer1 = Gamer.objects.create(user=user1)
        gamer2 = Gamer.objects.create(user=user2)
        
        friendship = Friendship.objects.create(sender=gamer1, receiver=gamer2, status='pe')
        
        self.client.login(username='user2', password='pass123')
        response = self.client.post(reverse('friends'), data={'decline': '1', 'solicitud': friendship.id})
        
        friendship.refresh_from_db()
        self.assertEqual(friendship.status, 'de')
        
        self.assertTemplateUsed(response, 'friends.html')

    def test_remove_friendship(self):
        user1 = User.objects.create_user('user1', password='pass123')
        user2 = User.objects.create_user('user2', password='pass123')
        gamer1 = Gamer.objects.create(user=user1)
        gamer2 = Gamer.objects.create(user=user2)
        
        friendship = Friendship.objects.create(sender=gamer1, receiver=gamer2, status='ac')
        
        Thread.objects.create(first_person=user1, second_person=user2)
        
        self.client.login(username='user2', password='pass123')
        response = self.client.post(reverse('friends'), data={'remove': '1', 'solicitud': friendship.id})
        
        self.assertFalse(Friendship.objects.filter(id=friendship.id).exists())
        self.assertFalse(Thread.objects.filter(id=1).exists())
        
        self.assertTemplateUsed(response, 'friends.html')

    def test_friends_view(self):
        user1 = User.objects.create_user('user1', password='pass123')
        user2 = User.objects.create_user('user2', password='pass123')
        gamer1 = Gamer.objects.create(user=user1)
        gamer2 = Gamer.objects.create(user=user2)
        
        friendship = Friendship.objects.create(sender=gamer1, receiver=gamer2, status='pe')
        
        self.client.login(username='user2', password='pass123')
        response = self.client.get(reverse('friends'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'friends.html')
        
        self.assertIn('solicitudes', response.context)
        self.assertIn('amigos', response.context)
        
        self.assertIn(friendship, response.context['solicitudes'])

# CreateReportView

class CreateReportViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_create_report_success(self):
        valid_form_data = {'user': self.user.id,'title': 'Test report','desc': 'Test report description','type': 'us'}
        form = ReportCreateForm(data=valid_form_data)

        response = self.client.post(reverse('report'), data=form.data, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Report.objects.count(), 1)

        report = Report.objects.first()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.title, 'Test report')
        self.assertEqual(report.desc, 'Test report description')
        self.assertEqual(report.type, 'us')
        self.assertIsNotNone(report.img)

        self.assertRedirects(response, reverse('index'))

        messages = list(response.context.get('messages'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your report has been sent.')

    def test_create_report_invalid_form(self):

        invalid_form_data = {'user': self.user.id,'title': '','desc': 'Test report description','type': 'us'}
        form = ReportCreateForm(data=invalid_form_data)

        response = self.client.post(reverse('report'), data=form.data, follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Report.objects.count(), 0)

        self.assertRedirects(response, reverse('report'))

        messages = list(response.context.get('messages'))
        self.assertEqual(len(messages), 1)

    def tearDown(self):
        self.client.logout()
        self.user.delete()

# ReportsView

class ReportsViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.report = Report.objects.create(title='Test Report', desc='This is a test report', type='us', user=self.user)

    def test_view_restricted_to_authenticated_users(self):
        self.client.logout()

        response = self.client.get(reverse('reports'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/web/authenticationlogin?next=/web/reports/')

    def test_view_loads_successfully_with_get(self):
        response = self.client.get(reverse('reports'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listreports.html')
        self.assertContains(response, 'Test Report')

    def test_reports_order_by_date(self):
        report_2 = Report.objects.create(title='Test Report 2', desc='This is another test report', type='bu', user=self.user)

        report_2.date = timezone.now() - timezone.timedelta(days=1)
        report_2.save()

        response = self.client.get(reverse('reports'), {'dateorder': 'desc'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'listreports.html')
        self.assertContains(response, 'Test Report 2')
        self.assertContains(response, 'Test Report')
        reports = response.context['reports']
        self.assertEqual(list(reports), [self.report, report_2])

    def test_reports_filter_by_title(self):
        Report.objects.create(title='Prueba de reporte', desc='Prueba', type='us', user=self.user)
        Report.objects.create(title='Reporte de prueba', desc='Prueba', type='he', user=self.user)
        Report.objects.create(title='Este no deberia aparecer', desc='Prueba', type='bu', user=self.user)

        response = self.client.get('/web/reports/?titulo=prueba')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prueba de reporte')
        self.assertContains(response, 'Reporte de prueba')
        self.assertNotContains(response, 'Este no deberia aparecer')

    def test_reports_filter_by_type(self):
        Report.objects.create(title='Prueba de reporte', desc='Prueba', type='bu', user=self.user)
        Report.objects.create(title='Reporte de prueba', desc='Prueba', type='he', user=self.user)
        Report.objects.create(title='Este no deberia aparecer', desc='Prueba', type='bu', user=self.user)

        response = self.client.get('/web/reports/?tipo=he')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Prueba de reporte')
        self.assertContains(response, 'Reporte de prueba')
        self.assertNotContains(response, 'Este no deberia aparecer')

    def test_reports_filter_by_user(self):
        user1 = User.objects.create_user('testuser1', password='12345')
        user2 = User.objects.create_user('testuser2', password='12345')
        self.client.login(username='testuser1', password='12345')

        Report.objects.create(title='Prueba de reporte', desc='Prueba', type='he', user=user1)
        Report.objects.create(title='Reporte de prueba', desc='Prueba', type='bu', user=user1)
        Report.objects.create(title='Este no deberia aparecer', desc='Prueba', type='us', user=user2)

        response = self.client.get('/web/reports/?usuario=testuser1')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prueba de reporte')
        self.assertContains(response, 'Reporte de prueba')
        self.assertNotContains(response, 'Este no deberia aparecer')

    def test_reports_filter_by_solved(self):
        staff_user = User.objects.create_user('staffuser', password='12345', is_staff=True)
        self.client.login(username='staffuser', password='12345')

        Report.objects.create(title='Prueba de reporte', desc='Prueba', type='he', user=staff_user, checked=True)
        Report.objects.create(title='Reporte de prueba', desc='Prueba', type='bu', user=staff_user, checked=False)
        Report.objects.create(title='Este no deberia aparecer', desc='Prueba', type='us', user=staff_user, checked=False)

        response = self.client.get('/web/reports/?solved=yes')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prueba de reporte')
        self.assertNotContains(response, 'Reporte de prueba')
        self.assertNotContains(response, 'Este no deberia aparecer')

# ReportDetailsView

class ReportDetailsViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.report = Report.objects.create(title='Test Report', desc='This is a test report', user=self.user, type='bu')
        self.clan = Clan.objects.create(name='Test Clan', description='This is a test clan',leader=self.user.username)
        self.gamer = Gamer.objects.create(user=self.user, clan=self.clan)
        self.url = reverse('reportdetails', kwargs={'report_id': self.report.id})

    def test_auth_user_can_access_view_(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reportdetails.html')

    def test_delete_clan_not_exist(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {'deleteclan': 'non_existing_clan'})
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'This clan does not exist.')

    def test_verify_user_not_exist(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {'verified': 'non_existing_user'})
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'This user does not exist.')

    def test_ban_user_not_exist(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {'banuser': 'Nonexistent User'})
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'This user does not exist.')

    def test_delete_clan(self):
        self.client.login(username='testuser', password='testpass')
        clan = Clan.objects.create(name='deleteme', description='Delete test clan',leader=self.user.username)
        response = self.client.post(self.url, {'deleteclan': 'deleteme'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reportdetails', args=[self.report.id]))
        self.assertFalse(Clan.objects.filter(name='deleteme').exists())
    
    def test_ban_user(self):
        self.client.login(username='testuser', password='testpass')
        user = User.objects.create_user(username='banme', password='12345')
        gamer = Gamer.objects.create(user=user, clan=self.clan)
        response = self.client.post(self.url, {'banuser': 'banme'})
        user.refresh_from_db()
        gamer.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reportdetails', args=[self.report.id]))
        self.assertFalse(user.is_active)
        self.assertIsNone(gamer.clan)

    def test_verify_user(self):
        self.client.login(username='testuser', password='testpass')
        user = User.objects.create_user(username='verifyme', password='12345')
        response = self.client.post(self.url, data={'verified': 'verifyme'})
        user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('reportdetails', args=[self.report.id]))
        self.assertTrue(user.verified)

    def test_mark_report_checked(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, {'checked': 'yes'})
        self.report.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.report.checked)