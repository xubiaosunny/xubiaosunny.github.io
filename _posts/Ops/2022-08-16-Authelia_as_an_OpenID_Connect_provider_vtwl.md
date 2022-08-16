---
layout: post
title: "Authelia为其他服务提供认证（以gitea为例）"
date: 2022-08-16 19:55:48 +0800
categories: 技术
tags: Authelia OpenID  OAuth
---

Authelia可以作为OIDC(OpenID Connect)服务，本文以`Gitea`为例记录一下如何进行配置。官方文档还介绍了`GitLab`、`Nextcloud`等其他多个服务的配置，具体可查看官方文档。

文中的`123456789ABEDEF`、`gitea.example.com`、 `auth.example.com`等注意替换为实际文本。


## Authelia配置

Authelia中通过`identity_providers`配置项来配置，一下为官方的例子。

```yaml
...
identity_providers:
  oidc:
    hmac_secret: this_is_a_secret_abc123abc123abc
    issuer_private_key: |
      -----BEGIN RSA PRIVATE KEY-----
      MXIEogIB$AKCAQEAxZVJP3WF//PG2fLQoEC9DtdiFG/+00vqlbVzz47nyxKONIPI
      lmL3UdmqpGTKMe/5Brqse4ZAKlQHiDbwzK9ypnfigtHuvh/JO0S7ChP70RC67ed1
      HV1nyfz5eW3llbtGJPrlYLqITNgctHp6zmRUFtSzPj9qFvozI93LJi492yL1+vu8
      Un3Dm8+Qq6XM2tPdEcldB/dtBwOWoF+8eOOVsu0TDuB5bwlhBVGJuSAuzBPRS2bF
      Ga4uk0JDdkDOMCEQxC5uWDFxgfERSMFyfLVWD47woDbuWEBq10c0z+dpWPMp7Ain
      YnnkqicwCN88Z0zid6MmMQ65F4+9Hc+qC/p6xwIDAQABAoIBAGlhaAHKor+Su3o/
      AXqXTL5/rbYMzbLQiLt0XeJT69jpeqMTroZXHmWvXE3128mqnf0yzw/K2Ko6yxGh
      i+j/onya8FqpsVYCCgfsbn2/js1AyRJeIp6Y1ORsYnqbXJnxmkXa80AV/OBPW2/+
      60TtSdQrebY3iFPc+i2k+9bPTvpyyDLKlz8UwdZG+k5uyYNIyQTccz+PjwsIvDij
      7tKYamhhLN3QXt3/aZTFpjTgezP4WyriZxjWrddHowc47q2rwNS95ND39JcysJAc
      0Pcbu8A5lVa7Fx33uOtzDfKWIW7xVEN+OtPgN+FbTjXcXk5IZedl+pW5lU5P++G/
      ZPvz+WECgYEA9g6HwdODW3e68bOqsFoKg35+vfUFMzlyMF8HFylNVfnLpTEDr637
      owzMFvcUxVd71b+gV5nnnbI+riUFIgyR8vhCjhy4moopDPahC4/KwN4NG6uz+i1h
      AB6D5+zn2BjnO/5xMMFGlApWtRNmJVGYlNDj3bXKh2VXzzy03VNeD8kCgYEAzZFL
      OlzoRB1HKpTWIECcuvxofMxLOLb3zs0k2t/FYNYIpovmGWCCAULz13y53e5+/+5m
      7I9VUZJFaIhaZ36qVBApCKdru69pZMkWCcQO9jELFcx51Ez7OgJWzu7GS1QJCPKC
      fEDxI0rZK21j93/Sl/nUnEir7CYpQ+wvCaGuHg8CgYAXgbncfY1+DokwkB6NbHy2
      pT4Mfbz6cNGE538w6kQ2I4AeDvmwLentYMqaow478CinegAiflSPTzkHwAemghbr
      ZGZPV1UXhn13fJRUG2+eT1hnPVcbXnx223N0k8Bud6qXo65CnyRT/kzcTbcjd5Eh
      Hne2daicmMTzynPo9Q72aQKBgBmobO9X8VWvIdbaxO85oVZlctVA2pK1o7CYQmVf
      UM+JZ4MCKzI3rYJizPS0iK5+ujNPmmEkcs2/qBIoEsCgOrpLWhPOcc/3UPxXbPzD
      D+sCrBOIdhxdj23qJNOnUfDNCGOpgUfpAzAYg4q8GKInvi1h7XukRnEvQi9MJ4LY
      P1dZAoGASGcGnTMkmeSXP8ux+dvQJAiJskn/sJIgBZ5uq5GRCeLBUosRSVxM75UK
      vAh/c/RBj+pYXVKuPuHGZCQJxsdcRXzXNGouUtgbaYML5Me/Hagt20QzDRBfuGBg
      qeZBJaXhjElvw6PUWtg4x+LYRCBpq/bS3LK3ozZrSTukVkKDegw=
      -----END RSA PRIVATE KEY-----
    access_token_lifespan: 1h
    authorize_code_lifespan: 1m
    id_token_lifespan: 1h
    refresh_token_lifespan: 90m
    enable_client_debug_messages: false
    enforce_pkce: public_clients_only
    cors:
      endpoints:
        - authorization
        - token
        - revocation
        - introspection
      allowed_origins:
        - https://example.com
      allowed_origins_from_client_redirect_uris: false
    clients:
      - id: myapp
        description: My Application
        secret: this_is_a_secret
        sector_identifier: ''
        public: false
        authorization_policy: two_factor
        pre_configured_consent_duration: ''
        audience: []
        scopes:
          - openid
          - groups
          - email
          - profile
        redirect_uris:
          - https://oidc.example.com:8080/oauth2/callback
        grant_types:
          - refresh_token
          - authorization_code
        response_types:
          - code
        response_modes:
          - form_post
          - query
          - fragment
        userinfo_signing_algorithm: none
....
```

1. 首先替换`hmac_secret`，使用官方推荐方法生产随机字符串替换

```bash
LENGTH=64
tr -cd '[:alnum:]' < /dev/urandom | fold -w "${LENGTH}" | head -n 1 | tr -d '\n' ; echo
```

2. 替换自己生成的`issuer_private_key`，用以下命令生成的`private.pem`中的内容粘贴替换

```bash
openssl genrsa -out private.pem 4096
openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```

3. 修改`allowed_origins`防止跨域，`*`代表所有域名，可替换为具体域名

```yaml
identity_providers:
  oidc:
    cors:
      allowed_origins:
        - "*"
```

4. 配置`clients`，添加`gitea`，注意替换自己的`secret`和`redirect_uris`

```yaml
identity_providers:
  oidc:
    clients:
      - id: gitea
        secret: 123456789ABEDEF
        public: false
        authorization_policy: two_factor
        scopes:
          - openid
          - email
          - profile
        redirect_uris:
          - https://gitea.example.com/user/oauth2/authelia/callback
        userinfo_signing_algorithm: none
```

## Gitea配置

1. 编辑`app.ini`

```ini
[openid]
ENABLE_OPENID_SIGNIN = false
ENABLE_OPENID_SIGNUP = true
WHITELISTED_URIS     = auth.example.com
```

2. 在Gitea后台添加认证源

![](/assets/images/post/截屏2022-08-16 11.30.53.png)

* `客户端 ID （键）` -> `id`
* `客户端密钥` -> `secret`
* `OpenID 连接自动发现 URL` 根据实际域名填写

## 其他

在使用openid认证之前，首先还是需要在gitea中创建同用户名的账号的，并且在第一次授权登录时需要和gitea账号进行一次绑定，以后就可以直接使用openid授权登录了。

## 参考链接

* https://www.authelia.com/configuration/identity-providers/open-id-connect/
* https://www.authelia.com/integration/openid-connect/introduction/