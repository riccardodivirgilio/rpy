# rpy
Collections of functional utilities

python3 -m pip install python-rpy

## Password manager

create a password by doing

`python3 -m rpy create_password`

create a folder to store passwords

`mkdir ~/.passwords/`

save those as ENV_VARIABLES

```
export PASS_DEFAULT_PASSWORD="SSXK6xR-9LI7L0VhIfOdRJh7t4_g4yqozHF9fIXgkNg="`
export PASS_DEFAULT_LOCATION="~/.passwords/"
```

get the default password by using an hash with the secret

```
python3 -m rpy pass facebook
> Copied to clipboard: !mBg7+lOKsbc4chxHeVmhIJuORi4=
```

renew the password and store it persistently on "~/.passwords/"
```
python3 -m rpy pass facebook --renew
> Copied to clipboard: !G_NPflm0NIVVUESMDJ2rwsNzpVDOZQSqKquImwy16uQ=
```

list all created password
```
python3 -m rpy pass
> facebook
```

delete the password and return the default password
```
python3 -m rpy pass facebook --delete
> Previous secret for facebook: !G_NPflm0NIVVUESMDJ2rwsNzpVDOZQSqKquImwy16uQ=
> Copied to clipboard: !mBg7+lOKsbc4chxHeVmhIJuORi4=
```

