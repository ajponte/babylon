# Use the official OpenBao image as a base
FROM openbao/openbao:latest

# Add any custom configurations or tools here
# For example, we might want to install curl for health checks
USER root
RUN apk add --no-cache curl bash

# Switch back to the openbao user
USER openbao

# Expose the default OpenBao port
EXPOSE 8200

# Set the default entrypoint
ENTRYPOINT ["bao"]
CMD ["server", "-config=/openbao/config/config.hcl"]
