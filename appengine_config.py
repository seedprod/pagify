def capability_middleware(application):
  def wsgi_app(environ, start_response):
    if not capabilities.CapabilitySet('datastore_v3').is_enabled():
      print_error_message(environ, start_response)
    else:
      environ['capabilities.read_only'] = capabilities.CapabilitySet('datastore_v3', capabilities=['write']).is_enabled()
      return application(environ, start_response)

  return wsgi_app
