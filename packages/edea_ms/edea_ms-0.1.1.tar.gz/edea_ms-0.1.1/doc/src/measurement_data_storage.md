# Measurement Data Storage

Storing measurement data comes with some unique issues, it's very heterogenous in a way that single data points can be a small numeric value to full blown images or even trace files many MB in size.

## Strategies

The following are some of the options explored

### Plain files

The easy way.

### Object Storage

Using a S3 compatible object store for storing and retreiving the files.

Advantages:

Easy to scale, different solutions and vendors available to choose from.

Disadvantages:

Added complexity, especially for hosting an instance.

### SQLite Archives

Per Team/User database containing the measurement data.

Advantages:

- Basically zero conf
- Backup and restore per user is very simple

Disadvantages:

- Esoteric-ish use of the database?
