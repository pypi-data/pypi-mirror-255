"""Generates CA and server certificates.
\nExample:
\n  pytls -n 'My CA' -s example.dev -s api.example.dev -d ./certs
"""
import os

import click

from pytls_ca.crypt import create_cert_file, create_key_file, generate_ca_cert, generate_server_cert


@click.command(help=__doc__)
@click.option("-n", "--ca-name", default="PyTLS CA", help="The subject for the CA certificate.")
@click.option("-s", "--services", multiple=True, help="The services for which to generate certificates.")
@click.option("-d", "--output-directory", default="certs", help="The directory to write the certificates to.")
def cli(ca_name, services, output_directory):
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Generate the CA certificate
    ca_key, ca_cert = generate_ca_cert(subject=ca_name)
    create_cert_file(ca_cert, "ca", output_directory)
    create_key_file(ca_key, "ca", output_directory)

    # Generate the server certificates for each service
    for service in services:
        service_key, service_cert = generate_server_cert(
            ca_key=ca_key,
            ca_cert=ca_cert,
            subject=service,
        )

        # Write the certificate and key to files
        create_cert_file(service_cert, service, output_directory)
        create_key_file(service_key, service, output_directory)

    click.echo("Certificates created successfully!")


if __name__ == "__main__":
    cli()
