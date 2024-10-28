RESET_PASSWORD_EMAIL_HTML_TEMPLATE: str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a; /* Dark background */
            color: #e0e0e0; /* Light text */
            margin: 0;
            padding: 0;
        }

        .container {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            background-color: #2a2a2a; /* Dark card background */
            padding: 20px;
            border: 1px solid #444; /* Dark border */
            border-radius: 0.5rem; /* Rounded corners */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        h1 {
            color: #ffffff; /* White text for heading */
            font-size: 24px;
            text-align: center;
        }

        p {
            line-height: 1.6;
            font-size: 16px;
            color: #b0b0b0; /* Muted text */
        }

        .verification-code {
            font-size: 24px;
            color: #ffcc00; /* Bright accent color */
            font-weight: bold;
            margin: 20px 0;
            text-align: center;
            background-color: #333; /* Dark popover background */
            padding: 10px;
            border-radius: 4px;
            display: inline-block;
        }

        .footer {
            font-size: 12px;
            color: #888; /* Muted footer text */
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Password Reset Request</h1>
        <p>Hello, {{user_name}}</p>
        <p>We received a request to reset your password. Use the code below to complete the reset process:</p>
        
        <div class="verification-code">{{otp_code}}</div>
        
        <p>Please enter this code on the password reset form. This code will expire in 5 minutes.</p>
        
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


EMAIL_VERIFICATION_HTML_TEMPLATE: str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a1a; /* Dark background */
            color: #e0e0e0; /* Light text */
            margin: 0;
            padding: 0;
        }

        .container {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            background-color: #2a2a2a; /* Dark card background */
            padding: 20px;
            border: 1px solid #444; /* Dark border */
            border-radius: 0.5rem; /* Rounded corners */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        h1 {
            color: #ffffff; /* White text for heading */
            font-size: 24px;
            text-align: center;
        }

        p {
            line-height: 1.6;
            font-size: 16px;
            color: #b0b0b0; /* Muted text */
        }

        .verification-code {
            font-size: 24px;
            color: #ffcc00; /* Bright accent color */
            font-weight: bold;
            margin: 20px 0;
            text-align: center;
            background-color: #333; /* Dark popover background */
            padding: 10px;
            border-radius: 4px;
            display: inline-block;
        }

        .footer {
            font-size: 12px;
            color: #888; /* Muted footer text */
            margin-top: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Email Verification</h1>
        <p>Hello, {{user_name}}</p>
        <p>Welcome to {{company_name}}! To complete your registration, please verify your email address using the code below:</p>
        
        <div class="verification-code">{{otp_code}}</div>
        
        <p>This code is valid for 5 minutes. If you did not create an account, you can safely ignore this email.</p>
        <p>Thank you for joining us!</p>
        
        <div class="footer">
            <p>If you have any questions, feel free to contact our support team.</p>
        </div>
    </div>
</body>
</html>
"""

def create_user_verification_email_template(user_name: str, one_time_password: str, company_name: str) -> str:
    """
    Creates an HTML email template for a user verification email.

    Args:
        user_name (str): The name of the user who needs to verify their email.
        one_time_password (str): The one-time password to verify the user's email.
        company_name (str): The name of the company that sent the email.

    Returns:
        str: The HTML email template with the provided values.
    """
    return (
        EMAIL_VERIFICATION_HTML_TEMPLATE.replace("{{user_name}}", user_name)
        .replace("{{otp_code}}", one_time_password)
        .replace("{{company_name}}", company_name)
    )

