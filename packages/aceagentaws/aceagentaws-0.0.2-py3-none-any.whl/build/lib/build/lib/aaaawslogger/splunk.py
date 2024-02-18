def add_splunk_properties(event):
    # Extract Splunk properties
    splunk_properties = event.pop('splunk', {})

    # Replace event['headers'] with splunk_properties if event['headers'] is empty
    if not event.get('headers'):
        event['headers'] = splunk_properties
    return event