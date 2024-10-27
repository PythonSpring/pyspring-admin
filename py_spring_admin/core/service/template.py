RESET_PASSWORD_EMAIL_HTML_TEMPLATE: str = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            color: #333;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            background-color: #fff;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        h1 {
            color: #333;
        }
        p {
            line-height: 1.5;
            font-size: 16px;
        }
        .verification-code {
            font-size: 20px;
            color: #007bff;
            font-weight: bold;
            margin: 20px 0;
            text-align: center;
        }
        .footer {
            font-size: 12px;
            color: #666;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Password Reset Request</h1>
        <p>Hello, {{user_name}}</p>
        <p>We received a request to reset your password. Use the code below to complete the reset process:</p>
        
        <div class="verification-code">{{otp_code}}</div>
        <p>Please enter this code on the password reset form. This code will expire in 1 hour.</p>
        
        <p>If you did not request a password reset, please ignore this email.</p>
        <p>Thanks,<br>The {{company_name}} Team</p>
        
        <div class="footer">
            <p>If you have any questions, feel free to contact our support team.</p>
        </div>
    </div>
</body>
</html>
"""


def create_reset_password_email_template(
    user_name: str, one_time_password: str, company_name: str
) -> str:
    """
    Creates an HTML email template for a password reset request.

    Args:
        user_name (str): The name of the user who requested the password reset.
        reset_link (str): The link to reset the user's password.
        company_name (str): The name of the company that sent the email.

    Returns:
        str: The HTML email template with the provided values.
    """
    return (
        RESET_PASSWORD_EMAIL_HTML_TEMPLATE.replace("{{user_name}}", user_name)
        .replace("{{otp_code}}", one_time_password)
        .replace("{{company_name}}", company_name)
    )
