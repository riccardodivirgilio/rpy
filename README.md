# Installation

`python3 -m pip install python-rpy`

## Password manager

create a password by doing

`python3 -m rpy create_password`

create a folder to store passwords

`mkdir ~/.passwords/`

export password manager settings and a shortcut

```
export PASS_DEFAULT_PASSWORD="MyVerySuperSecretPasswordBase64UrlSafeEncod" # The one that was created with python3 -m rpy create_password
export PASS_DEFAULT_LOCATION="~/.passwords/" # the directory you just created
alias pass="python3 -m rpy pass "
```

get the default password by using an hash with the secret

```
pass facebook
> Copied to clipboard: !mBg7+lOKsbc4chxHeVmhIJuORi4=
```

renew the password and store it persistently on "~/.passwords/"
```
pass facebook --renew
> Copied to clipboard: !6pBicHA2UtlorWb-criRrp7qVNf=
```

list all created password
```
pass
> facebook
```

delete the password and return the default password
```
pass facebook --delete
> Previous secret for facebook: !6pBicHA2UtlorWb-criRrp7qVNf=
> Copied to clipboard: !mBg7+lOKsbc4chxHeVmhIJuORi4=
```

