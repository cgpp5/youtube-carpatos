old_emails = {
    b"carlostellier@gmail.com",
    b"carlosgpp@proton.me",
}

if commit.author_email in old_emails:
    commit.author_name = b"cgpp5"
    commit.author_email = b"paniaguapalmero@gmail.com"

if commit.committer_email in old_emails:
    commit.committer_name = b"cgpp5"
    commit.committer_email = b"paniaguapalmero@gmail.com"
