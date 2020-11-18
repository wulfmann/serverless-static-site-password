# Serverless Static Site Password

This repo contains example code for implementing a static site password via AWS lambda@edge and CDK.

## Overview

When a request is made to the site, a lambda@edge (Viewer Certificate) is triggered by cloudfront. This lambda checks for the presence of a cookie that contains a signed token. It validates the signature and checks if it is expired. If it's valid, it allows the request. If the token is absent or invalid/expired, the request is redirected to the login page. The login page is configured to send the password to a `/_callback` route. When the lambda is triggered, it checks the request uri to see if it matched `_callback`. If it does, it validates the password and issues a new token. If the password is invalid, the request is blocked. The newly created token is passed back in the aforementioned cookie.