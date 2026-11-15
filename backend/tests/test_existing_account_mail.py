from services.mailer import templates


def test_the_existing_account_email_is_safe_and_helpful():
    mail = templates.existing_account_mail(
        to="a@b.com",
        full_name='<script>alert(1)</script> Neliswa',
        login_url='https://app.example.com/login?x="1"',
    )
    assert "<script>" not in mail.html and "&lt;script&gt;" in mail.html
    assert "&quot;" in mail.html
    assert "already have one" in mail.text
    assert "https://app.example.com/login" in mail.text
    assert mail.subject == "Someone tried to register your TradePilot AI email"
    assert "login code" not in mail.text.lower()
