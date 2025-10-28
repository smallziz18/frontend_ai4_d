"""
Templates HTML pour les emails
"""

def get_verification_email_template(username: str, verification_link: str) -> str:
    """Template HTML pour l'email de vérification"""
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vérification de compte</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .email-container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
        }}
        .message {{
            font-size: 16px;
            color: #555;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        .button-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .verify-button {{
            display: inline-block;
            padding: 15px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: transform 0.2s;
        }}
        .verify-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }}
        .alternative-link {{
            margin-top: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            font-size: 14px;
            color: #666;
        }}
        .alternative-link p {{
            margin: 5px 0;
        }}
        .alternative-link a {{
            color: #667eea;
            word-break: break-all;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            font-size: 14px;
            color: #888;
            border-top: 1px solid #eee;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        .warning {{
            margin-top: 30px;
            padding: 15px;
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
            font-size: 14px;
            color: #856404;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="icon">🚀</div>
            <h1>Bienvenue sur AI4D !</h1>
        </div>
        
        <div class="content">
            <div class="greeting">
                Bonjour <strong>{username}</strong> ! 👋
            </div>
            
            <div class="message">
                <p>Merci de vous être inscrit sur notre plateforme d'apprentissage de l'Intelligence Artificielle !</p>
                <p>Pour activer votre compte et commencer votre aventure, veuillez cliquer sur le bouton ci-dessous pour vérifier votre adresse email.</p>
            </div>
            
            <div class="button-container">
                <a href="{verification_link}" class="verify-button">
                    ✓ Vérifier mon compte
                </a>
            </div>
            
            <div class="alternative-link">
                <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
                <p><a href="{verification_link}">{verification_link}</a></p>
            </div>
            
            <div class="warning">
                ⚠️ <strong>Important :</strong> Ce lien expire dans <strong>24 heures</strong>. 
                Si vous n'avez pas créé de compte sur AI4D, ignorez simplement cet email.
            </div>
        </div>
        
        <div class="footer">
            <p><strong>AI4D - Plateforme d'apprentissage IA</strong></p>
            <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
            <p style="margin-top: 15px; color: #aaa;">© 2025 AI4D. Tous droits réservés.</p>
        </div>
    </div>
</body>
</html>
"""


def get_password_reset_email_template(username: str, reset_link: str) -> str:
    """Template HTML pour l'email de réinitialisation de mot de passe"""
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Réinitialisation de mot de passe</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .email-container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            color: #333;
            margin-bottom: 20px;
        }}
        .message {{
            font-size: 16px;
            color: #555;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        .button-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .reset-button {{
            display: inline-block;
            padding: 15px 40px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
            transition: transform 0.2s;
        }}
        .reset-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 87, 108, 0.6);
        }}
        .alternative-link {{
            margin-top: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            font-size: 14px;
            color: #666;
        }}
        .alternative-link p {{
            margin: 5px 0;
        }}
        .alternative-link a {{
            color: #f5576c;
            word-break: break-all;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            font-size: 14px;
            color: #888;
            border-top: 1px solid #eee;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        .security-notice {{
            margin-top: 30px;
            padding: 15px;
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
            font-size: 14px;
            color: #856404;
        }}
        .warning-box {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            border-radius: 4px;
            font-size: 14px;
            color: #721c24;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="icon">🔐</div>
            <h1>Réinitialisation de mot de passe</h1>
        </div>
        
        <div class="content">
            <div class="greeting">
                Bonjour <strong>{username}</strong>,
            </div>
            
            <div class="message">
                <p>Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte AI4D.</p>
                <p>Pour créer un nouveau mot de passe, cliquez sur le bouton ci-dessous :</p>
            </div>
            
            <div class="button-container">
                <a href="{reset_link}" class="reset-button">
                    🔑 Réinitialiser mon mot de passe
                </a>
            </div>
            
            <div class="alternative-link">
                <p>Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
                <p><a href="{reset_link}">{reset_link}</a></p>
            </div>
            
            <div class="security-notice">
                ⏰ <strong>Ce lien expire dans 1 heure</strong> pour votre sécurité.
            </div>
            
            <div class="warning-box">
                ⚠️ <strong>Vous n'avez pas demandé cette réinitialisation ?</strong><br>
                Si vous n'êtes pas à l'origine de cette demande, ignorez cet email. 
                Votre mot de passe actuel reste inchangé et sécurisé.
            </div>
        </div>
        
        <div class="footer">
            <p><strong>AI4D - Plateforme d'apprentissage IA</strong></p>
            <p>Pour toute question, contactez notre support.</p>
            <p style="margin-top: 15px; color: #aaa;">© 2025 AI4D. Tous droits réservés.</p>
        </div>
    </div>
</body>
</html>
"""


def get_welcome_email_template(username: str) -> str:
    """Template HTML pour l'email de bienvenue après vérification"""
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compte vérifié !</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .email-container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 20px;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }}
        .message {{
            font-size: 16px;
            color: #555;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        .features {{
            margin: 30px 0;
        }}
        .feature {{
            display: flex;
            align-items: start;
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }}
        .feature-icon {{
            font-size: 24px;
            margin-right: 15px;
        }}
        .feature-content h3 {{
            margin: 0 0 5px 0;
            color: #333;
            font-size: 16px;
        }}
        .feature-content p {{
            margin: 0;
            color: #666;
            font-size: 14px;
        }}
        .button-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .start-button {{
            display: inline-block;
            padding: 15px 40px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(56, 239, 125, 0.4);
            transition: transform 0.2s;
        }}
        .start-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(56, 239, 125, 0.6);
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            font-size: 14px;
            color: #888;
            border-top: 1px solid #eee;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        .icon {{
            font-size: 64px;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="icon">🎉</div>
            <h1>Compte vérifié avec succès !</h1>
        </div>
        
        <div class="content">
            <div class="greeting">
                Félicitations <strong>{username}</strong> ! 🎊
            </div>
            
            <div class="message">
                <p>Votre compte AI4D est maintenant actif et prêt à l'emploi !</p>
                <p>Vous pouvez commencer votre parcours d'apprentissage en Intelligence Artificielle dès maintenant.</p>
            </div>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-content">
                        <h3>Quiz personnalisés</h3>
                        <p>Des questions adaptées à votre niveau et vos objectifs</p>
                    </div>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">🏆</div>
                    <div class="feature-content">
                        <h3>Système de gamification</h3>
                        <p>Gagnez des XP, débloquez des badges et grimpez dans le classement</p>
                    </div>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">🔥</div>
                    <div class="feature-content">
                        <h3>Séries quotidiennes</h3>
                        <p>Maintenez votre streak et obtenez des bonus d'XP</p>
                    </div>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <div class="feature-content">
                        <h3>Analyse détaillée</h3>
                        <p>Suivez votre progression et identifiez vos points forts</p>
                    </div>
                </div>
            </div>
            
            <div class="button-container">
                <a href="http://localhost:8501" class="start-button">
                    🚀 Commencer maintenant
                </a>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>AI4D - Plateforme d'apprentissage IA</strong></p>
            <p>Besoin d'aide ? Contactez notre support à tout moment.</p>
            <p style="margin-top: 15px; color: #aaa;">© 2025 AI4D. Tous droits réservés.</p>
        </div>
    </div>
</body>
</html>
"""

