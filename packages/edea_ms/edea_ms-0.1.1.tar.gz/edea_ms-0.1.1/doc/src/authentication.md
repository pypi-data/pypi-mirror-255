# Authentication

The broad idea behind how edea-ms handles authentication and authorization is: do only what's absolutely necessary.
Nowadays there's so many login providers and authentication solutions etc. that it's a fools errand to try and guess what
someone will use and try to support and maintain that solution. It's even worse when one thinks of whatever internal solutions
have grown over time in some environments.

That's why we support two rather simple methods to authenticate a user: JWTs and HTTP headers. Only little information is required
to serve a user and luckily for JWTs there's commonly used fields which represent the information needed.
For HTTP headers there's no standards as to what the parameters should be called and from a cursory look at different authenticating
proxies, names vary a bit.

## Required Information and Fields

The following fields are supported:

| Field name | Header           | JWT    | Purpose                                           |
|------------|------------------|--------|---------------------------------------------------|
| username   | X-WebAuth-User   | sub    | Subject name, a unique user identifier            |
| groups     | X-WebAuth-Groups | groups | A list of group identifiers a user is a member of |
| roles      | X-WebAuth-Roles  | roles  | A list of roles a user has, e.g. "admin"          |

HTTP Header fields can either appear multiple times for roles and groups or can also be set to comma-separated values.

Technically, only the username field is required because groups and roles default to empty. No groups being available means that every user will be able to see each project. As for roles it means no user will have special priviledges, so no admin actions can be performed via the UI or API.

## User roles

A user can have zero or more of the following roles:

- default: read-write access to projects a user is a member of
  - depending on the settings, default and caretaker are equivalent. when using automation to create and update projects and specifications it's better to split out the responsibilities so that fields aren't accidentally modified in one place and not the other.
- backup: allows a user to download the whole database
- automation: allows a user to create/read/update/delete projects and specifications but not anything else.
  - this role is to support integration in other existing systems where project information is being managed.
- ready-only: can't modify any data or create new entries
- caretaker: can modify specifications and project settings

In case edea-ms is running in an environment where similar roles already exist but have different names they can be overriden in `core.authz.custom_role_mapping`. There is no simple configuration for this because this should not be done lightly and only when there's a need to integrate with existing systems.

## Example configurations

To provide the authentication information, we tested a few different open source solutions with edea-ms.

### Caddy

TODO

### Authelia

TODO
