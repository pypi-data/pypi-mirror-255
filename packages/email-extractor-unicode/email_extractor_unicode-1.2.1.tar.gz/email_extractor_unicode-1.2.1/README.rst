<h1>Email Extractor Unicode</h1>
<p>Email Extractor Unicode is a Python library that allows you to extract emails from web pages related to phone
   numbers. It utilizes the undetected_chromedriver library to browse web pages and extract emails using regular
   expressions.
</p>
<h2>Installation</h2>
<p>To install Email Extractor Unicode, you can use pip:</p>
<pre><code>pip install email-extractor-unicode</code></pre>
<h2>Usage</h2>
<p>To use the library, you can import the <code>checker</code> function from the package.</p>
<pre><code>
import os
import subprocess

try:
    from email_extractor_unicode import checker
except ImportError:
    try:
        subprocess.check_call(["pip", "install", "email-extractor-unicode"])
        from email_extractor_unicode import checker
    except Exception as e:
        raise ImportError("Failed to install or import email-extractor-unicode:", e)

checker()
</code></pre>
<h2>Contact</h2>
<p>For any inquiries or feedback, you can reach out to me on Telegram at <a href="https://t.me/iamunicode"
   target="_blank">@iamunicode</a>. I'd be happy to hear from you and assist with any questions or issues
   related to Email Extractor Unicode.
</p>
<h2>Disclaimer</h2>
<p>Please use this library responsibly and respect the terms of service of the websites you are scraping. Email
   extraction from websites may be subject to legal restrictions in some jurisdictions. Always ensure you have the
   right to extract data from the websites you visit.
</p>

<h2>Change Log</h2>
<ul>
    <li><strong>1.2.1 (02/06/2024)</strong></li>
    <ul>
        <li>Saves Phone Number:Email</li>
        <li>Saves Emails</li>
        <li>Saves processed phone numbers</li>
    </ul>
</ul>
