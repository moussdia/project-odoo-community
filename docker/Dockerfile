FROM debian:buster-slim
LABEL vendor="veone/odoo/ce" maintainer="dev@veone.net" version="1.0.0"

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates=20200601~deb10u2 \
        curl=7.64.0-4+deb10u2 \
        dirmngr=2.2.12-1+deb10u1 \
        fonts-noto-cjk=1:20170601+repack1-3+deb10u1 \
        gnupg=2.2.12-1+deb10u1 \
        libssl-dev=1.1.1d-0+deb10u7 \
        node-less=1.6.3~dfsg-3 \
        npm=5.8.0+ds6-4+deb10u2 \
        python3-num2words=0.5.6-1 \
        python3-pdfminer=20181108+dfsg-3 \
        python3-pip=18.1-5 \
        python3-phonenumbers=8.9.10-1 \
        python3-pyldap=3.1.0-2 \
        python3-qrcode=6.1-1 \
        python3-renderpm=3.5.13-1+deb10u1 \
        python3-setuptools=40.8.0-1 \
        python3-slugify=2.0.1-1 \
        python3-vobject=0.9.6.1-0.1 \
        python3-watchdog=0.9.0-1 \
        python3-xlrd=1.1.0-1 \
        python3-xlwt=1.3.0-2 \
        xz-utils=5.2.4-1 \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.buster_amd64.deb \
    && echo 'ea8277df4297afc507c61122f3c349af142f31e5 wkhtmltox.deb' | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client=11+200+deb10u4 \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

# Install rtlcss (on Debian buster)
RUN npm install -g rtlcss@3.1.2

# Install Odoo
ARG ODOO_VERSION=14.0
ARG ODOO_RELEASE=20210427
ARG ODOO_SHA=9d8e8038d5589bc8f4f5f012773dba4deefd3adc

RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
    && echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \
    && apt-get update \
    && apt-get -y install --no-install-recommends ./odoo.deb \
    && rm -rf /var/lib/apt/lists/* odoo.deb

# Copy entrypoint script and Odoo configuration file
COPY ./docker/wait-for-psql.py /usr/local/bin/wait-for-psql.py
COPY ./docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY ./docker/odoo.conf /etc/odoo/

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/veone-addons for users addons
RUN mkdir -p /mnt/extra-addons /mnt/veone-addons \
    && chown -R odoo /etc/odoo/odoo.conf /mnt/extra-addons /mnt/veone-addons \
	&& chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/wait-for-psql.py

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

ENTRYPOINT ["entrypoint.sh"]
CMD ["odoo"]

COPY ./addons /mnt/veone-addons
COPY ./config /etc/odoo

# Set default user when running the container
USER odoo
