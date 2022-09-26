#!/bin/bash
#
# This will sync everything from A to B, and can be run multiple times,
# ensuring that if something is deleted from A, it will be deleted from B too!
# (FULL SYNC) Suitable only for backups
imapsync \
    --host1 A-mail.example.com --user1 john --password1 surethisisapassword \
    --host2 B-mail.example.com --user2 johndoe --password2 notapasswdaswell --delete2

