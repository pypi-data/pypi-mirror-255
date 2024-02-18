// Based on code from the 'kollect' package
//    https://github.com/davidsbond/kollect
// available under the following license:
//
//   Copyright 2021 David Bond
//
//    Licensed under the Apache License, Version 2.0 (the "License");
//    you may not use this file except in compliance with the License.
//    You may obtain a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
//    Unless required by applicable law or agreed to in writing, software
//    distributed under the License is distributed on an "AS IS" BASIS,
//    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//    See the License for the specific language governing permissions and
//    limitations under the License.

package main

import (
	"context"
	"flag"
	"os"
	"os/signal"
	"syscall"

	"golang.org/x/sync/errgroup"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
	"k8s.io/klog/v2"

	"gitlab.com/ul-dsri/dyff/apps/workflows_informer/agent"
)

func main() {
	dryrun := flag.Bool("dryrun", false, "Log events but don't produce to Kafka")
	waitForSync := flag.Bool("waitforsync", false, "Wait for cache sync before processing events")
	flag.Parse()

	var namespace string = os.Getenv("DYFF_KUBERNETES__WORKFLOWS_NAMESPACE")
	var kafkaBootstrapServers string = os.Getenv("DYFF_KAFKA__CONFIG__BOOTSTRAP_SERVERS")
	var kafkaWorkflowsEventsTopic string = os.Getenv("DYFF_KAFKA__TOPICS__WORKFLOWS_EVENTS")
	var kubeConfigPath string = os.Getenv("KUBECONFIG")

	k8sConfig, err := agent.GetKubernetesConfig(kubeConfigPath)
	if err != nil {
		klog.Errorf("failed to create k8s config: %w", err)
	}

	client, err := dynamic.NewForConfig(k8sConfig)
	if err != nil {
		klog.Errorf("failed to create dynamic k8s client: %w", err)
	}
	cfg := agent.AgentConfig{
		Namespace:        namespace,
		ClusterClient:    client,
		WaitForCacheSync: *waitForSync,
		Resources: []schema.GroupVersionResource{
			{Group: "dyff.io", Version: "v1alpha1", Resource: "audits"},
			{Group: "dyff.io", Version: "v1alpha1", Resource: "datasets"},
			{Group: "dyff.io", Version: "v1alpha1", Resource: "evaluations"},
			{Group: "dyff.io", Version: "v1alpha1", Resource: "inferenceservices"},
			{Group: "dyff.io", Version: "v1alpha1", Resource: "inferencesessions"},
			{Group: "dyff.io", Version: "v1alpha1", Resource: "models"},
			{Group: "dyff.io", Version: "v1alpha1", Resource: "reports"},
		},
		KafkaBootstrapServers: kafkaBootstrapServers,
		KafkaClientId:         "dyff.workflows.informer",
		KafkaEventsTopic:      kafkaWorkflowsEventsTopic,
		DryRun:                *dryrun,
	}

	ctx, cancel := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer cancel()

	ag := agent.New(cfg)
	grp, ctx := errgroup.WithContext(ctx)
	grp.Go(func() error {
		return ag.Run(ctx)
	})

	if err := grp.Wait(); err != nil {
		klog.Errorf("error in Wait(): %w", err)
		os.Exit(1)
	}
}
