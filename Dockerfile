# Use the official Frappe Bench image
FROM frappe/bench:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    BENCH_DIR=/home/frappe/frappe-bench

USER root
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe

# Initialize a new bench
RUN bench init --skip-redis-config-generation --skip-assets --python python3 frappe-bench

WORKDIR ${BENCH_DIR}

# Download Frappe and ERPNext core apps (version-15)
RUN bench get-app --branch version-15 frappe --skip-assets
RUN bench get-app --branch version-15 erpnext --skip-assets

# Copy your custom app from the build context (apps/vj_biofuel repo)
# When building from the app repo, '.' is the root of vj_biofuel
COPY --chown=frappe:frappe . apps/vj_biofuel

# Install the custom app into the bench
RUN bench get-app vj_biofuel apps/vj_biofuel --skip-assets

# Build assets for all apps
RUN bench build --app frappe,erpnext,vj_biofuel

# Expose the port for Cloud Run
EXPOSE 8080

# Start the web server
CMD bench serve --port ${PORT:-8080}
