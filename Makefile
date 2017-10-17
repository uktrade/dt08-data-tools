openshift-create:
	oc process -f deployment/openshift/test-build-template.yml | oc create -f -

openshift-build-from-local:
	oc start-build dt08-test-build --from-dir=.
