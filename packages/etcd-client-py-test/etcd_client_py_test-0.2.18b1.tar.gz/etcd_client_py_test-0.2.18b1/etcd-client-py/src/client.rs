use etcd_client::{Client as EtcdClient, ConnectOptions};
use pyo3::prelude::*;
use pyo3::types::PyTuple;
use pyo3_asyncio::tokio::future_into_py;
use std::time::Duration;

use crate::communicator::PyCommunicator;
use crate::error::PyClientError;
use crate::lock_manager::{EtcdLockManager, PyEtcdLockOption};

#[pyclass(name = "ConnectOptions")]
#[derive(Clone, Default)]
pub struct PyConnectOptions(pub ConnectOptions);

#[pymethods]
impl PyConnectOptions {
    #[new]
    fn new() -> Self {
        Self(ConnectOptions::new())
    }

    fn with_user(&self, name: String, password: String) -> Self {
        PyConnectOptions(self.0.clone().with_user(name, password))
    }

    fn with_keep_alive(&self, interval: f64, timeout: f64) -> Self {
        PyConnectOptions(self.0.clone().with_keep_alive(
            Duration::from_secs_f64(interval),
            Duration::from_secs_f64(timeout),
        ))
    }

    fn with_keep_alive_while_idle(&self, enabled: bool) -> Self {
        PyConnectOptions(self.0.clone().with_keep_alive_while_idle(enabled))
    }

    fn with_connect_timeout(&self, connect_timeout: f64) -> Self {
        PyConnectOptions(
            self.0
                .clone()
                .with_connect_timeout(Duration::from_secs_f64(connect_timeout)),
        )
    }

    fn with_timeout(&self, timeout: f64) -> Self {
        PyConnectOptions(
            self.0
                .clone()
                .with_timeout(Duration::from_secs_f64(timeout)),
        )
    }

    fn with_tcp_keepalive(&self, tcp_keepalive: f64) -> Self {
        PyConnectOptions(
            self.0
                .clone()
                .with_tcp_keepalive(Duration::from_secs_f64(tcp_keepalive)),
        )
    }

    // TODO: Implement "tls", "tls-openssl" authentification
}

#[pyclass(name = "Client")]
#[derive(Clone)]
pub struct PyClient {
    pub endpoints: Vec<String>,
    pub options: PyConnectOptions,
    pub lock_options: Option<PyEtcdLockOption>,
}

#[pymethods]
impl PyClient {
    #[new]
    fn new(
        endpoints: Vec<String>,
        options: Option<PyConnectOptions>,
        lock_options: Option<PyEtcdLockOption>,
    ) -> Self {
        let options = options.unwrap_or(PyConnectOptions::default());
        Self {
            endpoints,
            options,
            lock_options,
        }
    }

    fn connect(&self, options: Option<PyConnectOptions>) -> Self {
        let mut result = self.clone();
        result.options = options.unwrap_or(self.options.clone());
        result
    }

    fn with_lock(&self, lock_options: PyEtcdLockOption, options: Option<PyConnectOptions>) -> Self {
        let mut result = self.clone();
        result.options = options.unwrap_or(self.options.clone());
        result.lock_options = Some(lock_options);
        result
    }

    fn __aenter__<'a>(&'a self, py: Python<'a>) -> PyResult<&'a PyAny> {
        let endpoints = self.endpoints.clone();
        let options = self.options.clone();
        let with_lock = self.lock_options.clone();
        future_into_py(py, async move {
            let client_result = EtcdClient::connect(endpoints, Some(options.0)).await;
            match client_result {
                Ok(client) => {
                    if with_lock.is_some() {
                        let mut lock_manager = EtcdLockManager::new(client, with_lock.unwrap());
                        Ok(lock_manager.handle_aenter().await?)
                    } else {
                        Ok(PyCommunicator::new(client))
                    }
                }
                Err(e) => Err(PyClientError(e).into()),
            }
        })
    }

    #[pyo3(signature = (*_args))]
    fn __aexit__<'a>(&'a self, py: Python<'a>, _args: &PyTuple) -> PyResult<&'a PyAny> {
        let endpoints = self.endpoints.clone();
        let options = self.options.clone();
        let with_lock = self.lock_options.clone();
        future_into_py(py, async move {
            if with_lock.is_some() {
                let client_result = EtcdClient::connect(endpoints, Some(options.0)).await;
                match client_result {
                    Ok(client) => {
                        let mut lock_manager = EtcdLockManager::new(client, with_lock.unwrap());
                        return Ok(lock_manager.handle_aexit().await?);
                    }
                    Err(e) => return Err(PyClientError(e).into()),
                }
            }
            Ok(())
        })
    }
}
