openshift-create:
	oc process -f build/openshift/test-build-template.yml | oc create -f -
