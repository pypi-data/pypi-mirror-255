class DeferredPromise {
  resolve;

  reject;

  promise = new Promise((resolve, reject) => {
    this.reject = reject;
    this.resolve = resolve;
  });
}

const octostar = {
  queue: [],
  listeners: {},
  channel: {
    postMessage: (message) => {
      console.log("queuing");
      window.octostar.queue.push(message);
    },
  },

  on(topic, callback) {
    this.listeners[topic] = this.listeners[topic] || [];
    this.listeners[topic].push(callback);
    return this.listeners[topic].length === 1;
  },

  off(topic, callback) {
    this.listeners[topic] = (this.listeners[topic] || []).filter(
      (cb) => cb !== callback
    );
    if (this.listeners[topic].length === 0) {
      delete this.listeners[topic];
      return true;
    }
    return false;
  },

  emit(topic, ...args) {
    const message = {
      isOctostarMessage: true,
      emit: topic,
      arguments: args,
      replyTo: `${topic}-once-${Math.random()}`,
    };
    const deferred = new DeferredPromise();
    const callback = deferred.resolve;
    this.once(message.replyTo, callback);
    window.octostar.channel.postMessage(message);
    return deferred.promise;
  },

  once(topic, callback) {
    const off = this.off.bind(this);
    const cb = function (data) {
      off(topic, cb);
      callback(data);
    };
    this.on(topic, cb);
  },

  callReplyingTo(topic, replyTo, ...args) {
    const message = {
      isOctostarMessage: true,
      call: topic,
      arguments: args,
      replyTo: replyTo,
    };
    const deferred = new DeferredPromise();
    const callback = deferred.resolve;
    this.once(message.replyTo, callback);

    window.octostar.channel.postMessage(message);
    return deferred.promise;
  },

  call(topic, ...args) {
    return this.callReplyingTo(
      topic,
      `${topic}-once-${Math.random()}`,
      ...args
    );
  },

  listen(topic, callback) {
    this.on(topic, callback);
    return () => this.unsubscribe(topic, callback);
  },

  subscribe(topic, callback) {
    if (this.on(topic, callback)) {
      const message = {
        isOctostarMessage: true,
        subscribe: topic,
        replyTo: topic,
      };
      window.octostar.channel.postMessage(message);
    }
    return () => this.unsubscribe(topic, callback);
  },

  unsubscribe(topic, callback) {
    if (this.off(topic, callback)) {
      const message = {
        isOctostarMessage: true,
        unsubscribe: topic,
        replyTo: `unsubscribed-${topic}`,
      };
      window.octostar.channel.postMessage(message);
    }
  },
};
const octostarAckListener = function (event) {
  if (event.data?.isOctostarMessage && event.data?.channel) {
    console.log("adding a listener");
    // window.removeEventListener("message", octostarAckListener);
    // window.parent.removeEventListener("message", octostarAckListener);
    window.octostar.channel = event.ports[0];
    window.octostar.channel.onmessageerror = (error) => {
      console.log("message channel error", error);
    };
    window.octostar.channel.onmessage = (message) => {
      const topic = message.data?.to;
      if (!topic) {
        console.log('no message "to" found for message', message);
        return;
      }
      if (topic === "ping") {
        console.log("ping");
        window.octostar.channel.postMessage({
          isOctostarMessage: true,
          call: "pong",
        });
        return;
      }

      const listeners = window.octostar.listeners[topic] || [];
      if (listeners.length === 0) {
        console.log(`no listeners for octostar message of type=${topic}`);
      }
      // TODO: handle message.data.exception

      let data = message.data.data;
      if (message.data.json) {
        data = JSON.parse(data);
      }
      listeners.forEach((listener) => listener(data));
    };
    window.octostar.channel.postMessage({
      isOctostarMessage: true,
      call: "ack",
    });
    while (window.octostar.queue.length) {
      window.octostar.channel.postMessage(window.octostar.queue.shift());
    }
  }
};

if (!window.octostar) {
  try {
    window.octostar = window.parent.octostar;
  } catch (e) {
    // pass
  }
}
window.octostar = window.octostar || octostar;

try {
  window.parent.octostar = window.parent.octostar || window.octostar;
} catch {
  // pass
}
if (!window.parent?.os_listener_added) {
  try {
    window.parent.addEventListener("message", octostarAckListener);
    window.parent.os_listener_added = true;
  } catch (e) {
    if (!window.os_listener_added) {
      window.addEventListener("message", octostarAckListener);
      window.os_listener_added = true;
    }
  }
}
