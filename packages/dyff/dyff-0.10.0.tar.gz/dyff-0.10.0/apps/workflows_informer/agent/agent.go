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

// Package agent provides the implementation of the in-cluster agent that reacts to resource changes and sends data
// to a configured event bus.
package agent

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"sync"
	"time"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	"golang.org/x/exp/slices"
	"golang.org/x/sync/errgroup"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/dynamic/dynamicinformer"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/cache"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/klog/v2"
)

// Config returns a rest.Config instance configured to use the kube config file located at the given path. If the
// kubeConfig parameter is blank, an in-cluster configuration is assumed.
func GetKubernetesConfig(kubeConfigPath string) (*rest.Config, error) {
	var err error
	var clusterConfig *rest.Config
	if kubeConfigPath != "" {
		clusterConfig, err = clientcmd.BuildConfigFromFlags("", kubeConfigPath)
	} else {
		clusterConfig, err = rest.InClusterConfig()
	}
	if err != nil {
		return nil, err
	}

	return clusterConfig, nil
}

// The Config type describes configuration values that can be set for the Agent.
type AgentConfig struct {
	// The Namespace that resources will be collected for.
	Namespace string
	// The configuration for the cluster.
	ClusterClient dynamic.Interface
	// The resource types to send via the EventWriter.
	Resources []schema.GroupVersionResource
	// If true, no events are published until the initial informer caches are synced. This prevents events being
	// publishing describing the current state.
	WaitForCacheSync bool

	KafkaBootstrapServers string

	KafkaClientId string

	KafkaEventsTopic string

	DryRun bool
}

// The Agent type is responsible for handling changes in resources within a cluster namespace and sending them
// to a configured EventWriter.
type Agent struct {
	config AgentConfig

	producer *kafka.Producer

	// Flag used to prevent event writing until informer caches are synced.
	synced bool

	// Mutex used to ensure only a single handler is invoked at a time. For example, to prevent update events
	// being published before creation event.
	handlerMux *sync.Mutex

	// Mutex used to get/set the synced flag across multiple goroutines.
	syncMux *sync.RWMutex
}

type StatusReason struct {
	Status string `json:"status"`
	Reason string `json:"reason"`
}

// New returns a new instance of the Agent type with a set Config.
func New(config AgentConfig) *Agent {
	producer, err := kafka.NewProducer(&kafka.ConfigMap{
		"bootstrap.servers":  config.KafkaBootstrapServers,
		"client.id":          config.KafkaClientId,
		"acks":               "all",
		"enable.idempotence": true,
	})
	if err != nil {
		klog.Errorf("failed to create kafka producer")
		return nil
	}

	return &Agent{
		config:     config,
		producer:   producer,
		handlerMux: &sync.Mutex{},
		syncMux:    &sync.RWMutex{},
	}
}

var errCacheSyncFailed = errors.New("failed to sync cache")

// Run starts the agent, any detected changes in cluster resources will be sent to the configured EventWriter. Blocks until
// an error occurs or until the provided context.Context is cancelled.
func (a *Agent) Run(ctx context.Context) error {

	factory := dynamicinformer.NewFilteredDynamicSharedInformerFactory(a.config.ClusterClient, time.Minute*5, a.config.Namespace, nil)
	group, ctx := errgroup.WithContext(ctx)

	cacheSyncs := make([]cache.InformerSynced, len(a.config.Resources))
	for i, rs := range a.config.Resources {
		informer := factory.ForResource(rs).Informer()
		cacheSyncs[i] = informer.HasSynced

		handler := a.informerHandler(ctx, informer)
		group.Go(handler)
	}

	// Cache sync can be disabled if users want to build an initial state. Ideally this is only used to start with
	// then disabled.
	if !a.config.WaitForCacheSync {
		a.syncMux.Lock()
		a.synced = true
		a.syncMux.Unlock()

		return group.Wait()
	}

	// Return value from WaitForCacheSync is not assigned to a.synced directly within the Lock() and Unlock().
	// This is because handler functions are invoked while caches are syncing. If we lock around cache.WaitForCacheSync
	// the initial invocations of the add, update and delete handlers will still be waiting for the lock to be freed.
	// causing all those unwanted invocations to trigger events.
	synced := cache.WaitForCacheSync(ctx.Done(), cacheSyncs...)

	// Prevent any events from being written until the initial caches are synced. This prevents rewriting the entire
	// state of the cluster/namespace should the agent restart.
	a.syncMux.Lock()
	a.synced = synced
	a.syncMux.Unlock()

	if !a.Ready() {
		return errCacheSyncFailed
	}

	return group.Wait()
}

func (a *Agent) informerHandler(ctx context.Context, informer cache.SharedIndexInformer) func() error {
	return func() error {
		ctx, cancel := context.WithCancel(ctx)
		defer cancel()

		informer.AddEventHandler(cache.ResourceEventHandlerFuncs{
			// AddFunc:    a.addHandler(ctx),
			UpdateFunc: a.updateHandler(ctx),
			DeleteFunc: a.deleteHandler(ctx),
		})
		err := informer.SetWatchErrorHandler(func(_ *cache.Reflector, err error) {
			// If we don't have access to this resource, log and stop the informer so that we don't pollute the logs
			// doing this over and over again.
			klog.Errorln(err)
			cancel()
		})
		if err != nil {
			return fmt.Errorf("failed to set watch error handler: %w", err)
		}

		go informer.Run(ctx.Done())
		<-ctx.Done()
		return nil
	}
}

var terminalStatuses []string = []string{"Ready", "Complete", "Failed", "Error", "Terminated"}

func isTerminalStatus(status string) bool {
	return slices.Contains(terminalStatuses, status)
}

func (a *Agent) getStatusReason(item *unstructured.Unstructured) (*StatusReason, error) {
	conditions, found, err := unstructured.NestedSlice(item.Object, "status", "conditions")
	if !found {
		// status.conditions can be missing in the initial state
		return nil, nil
	}
	if err != nil {
		klog.Errorf("%s: failed to access status.conditions", item.GetName())
		return nil, errors.New(fmt.Sprintf("%s: failed to access status.conditions (%v)", item.GetName(), err))
	}
	var terminalStatus *StatusReason = nil
	var transientStatus *StatusReason = nil
	for _, condition := range conditions {
		conditionMap := condition.(map[string]interface{})
		conditionType := conditionMap["type"].(string)
		if isTerminalStatus(conditionType) {
			if conditionMap["status"].(string) == "True" {
				terminalStatus = &StatusReason{
					Status: conditionType,
					Reason: conditionMap["reason"].(string),
				}
				break
			}
		} else if "Available" == conditionType {
			if conditionMap["status"].(string) == "True" {
				transientStatus = &StatusReason{
					Status: conditionType,
					Reason: conditionMap["reason"].(string),
				}
			}
		}
	}

	if terminalStatus != nil {
		return terminalStatus, nil
	} else if transientStatus != nil {
		return transientStatus, nil
	} else {
		return nil, nil
	}
}

func (a *Agent) getId(item *unstructured.Unstructured) (string, error) {
	id, found, err := unstructured.NestedString(item.Object, "spec", "id")
	if !found {
		return "", errors.New(fmt.Sprintf("%s: resource has no spec.id field", item.GetName()))
	}
	if err != nil {
		klog.Errorf("%s: failed to access spec.id", item.GetName())
		return "", errors.New(fmt.Sprintf("%s: failed to access spec.id (%v)", item.GetName(), err))
	}
	return id, nil
}

func (a *Agent) getStatusEventMessage(obj interface{}) *kafka.Message {
	item, ok := obj.(*unstructured.Unstructured)
	if !ok {
		klog.Errorf("item is not *unstructured.Unstructured:\n%+v", obj)
		return nil
	}

	id, err := a.getId(item)
	if err != nil {
		klog.Errorf("failed to get id for resource:\n%+v", item)
		return nil
	}

	statusReason, err := a.getStatusReason(item)
	if err != nil {
		klog.Errorf("failed to get status.conditions for resource:\n%+v", item)
		return nil
	}
	if statusReason == nil {
		// The current status is not relevant and should not be reported
		return nil
	}

	return a.marshalMessage(id, *statusReason)
}

func (a *Agent) marshalMessage(id string, statusReason StatusReason) *kafka.Message {
	msgValue, err := json.Marshal(statusReason)
	if err != nil {
		klog.Errorf("json marshal error:\n%+v", statusReason)
		return nil
	}

	msgKey := []byte(id)

	return &kafka.Message{
		TopicPartition: kafka.TopicPartition{
			Topic:     &a.config.KafkaEventsTopic,
			Partition: kafka.PartitionAny,
		},
		Key:   msgKey,
		Value: msgValue,
	}
}

const nullId string = "00000000000000000000000000000000"

func (a *Agent) produce(msg *kafka.Message) error {
	if string(msg.Key) == nullId {
		// These are dyff resources that are owned by other dyff resources;
		// they aren't independent entities and their status isn't tracked
		return nil
	}
	klog.Infof("produce: %v:%v", string(msg.Key), string(msg.Value))
	if a.config.DryRun {
		return nil
	} else {
		return a.producer.Produce(msg, nil)
	}
}

func (a *Agent) addHandler(ctx context.Context) func(obj interface{}) {
	return func(obj interface{}) {
		if !a.Ready() {
			return
		}

		a.handlerMux.Lock()
		defer a.handlerMux.Unlock()

		msg := a.getStatusEventMessage(obj)
		if msg == nil {
			return
		}

		err := a.produce(msg)
		if err != nil {
			klog.ErrorS(err, "produce failed")
			return
		}
	}
}

func (a *Agent) updateHandler(ctx context.Context) func(then, now interface{}) {
	return func(x, y interface{}) {
		if !a.Ready() {
			return
		}

		a.handlerMux.Lock()
		defer a.handlerMux.Unlock()

		xmsg := a.getStatusEventMessage(x)
		ymsg := a.getStatusEventMessage(y)

		if ymsg == nil {
			klog.Info("new status was nil")
			return
		}

		klog.Infof("new status: %v:%v", string(ymsg.Key), string(ymsg.Value))
		if xmsg != nil {
			klog.Infof("old status: %v:%v", string(xmsg.Key), string(xmsg.Value))
			if bytes.Compare(xmsg.Key, ymsg.Key) != 0 {
				klog.Errorf("old and new resources had different .id:\n%+v\n%+v", *xmsg, *ymsg)
				return
			}
			if bytes.Compare(xmsg.Value, ymsg.Value) == 0 {
				// No status change
				klog.Info("no status change")
				return
			}
		}

		err := a.produce(ymsg) // New status
		if err != nil {
			klog.ErrorS(err, "produce failed")
			return
		}
	}
}

func (a *Agent) deleteHandler(ctx context.Context) func(obj interface{}) {
	return func(obj interface{}) {
		if !a.Ready() {
			return
		}

		a.handlerMux.Lock()
		defer a.handlerMux.Unlock()

		item, ok := obj.(*unstructured.Unstructured)
		if !ok {
			klog.Errorf("item is not *unstructured.Unstructured:\n%+v", obj)
			return
		}

		statusReason, err := a.getStatusReason(item)
		if err != nil {
			klog.Errorf("failed to get (status, reason) for resource:\n%+v", item)
			return
		}
		if statusReason != nil && isTerminalStatus(statusReason.Status) {
			// Already in terminal status, so that's the final state
			return
		}

		// Resource was deleted while in a non-terminal status
		teminatedStatus := StatusReason{
			Status: "Terminated",
			Reason: "KubernetesResourceDeleted",
		}

		id, err := a.getId(item)
		if err != nil {
			klog.Errorf("failed to get id for resource:\n%+v", item)
			return
		}

		msg := a.marshalMessage(id, teminatedStatus)
		err = a.produce(msg)
		if err != nil {
			klog.ErrorS(err, "produce failed")
			return
		}
	}
}

// Ready returns true if the Agent's informer caches are synchronised.
func (a *Agent) Ready() bool {
	a.syncMux.RLock()
	defer a.syncMux.RUnlock()
	return a.synced
}
