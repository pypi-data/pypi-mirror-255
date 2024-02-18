use crate::{
    client::PyClient, communicator::PyCommunicator, error::{LockError, PyClientError}
};
use etcd_client::Client as EtcdClient;

use pyo3::prelude::*;
use std::time::Duration;
use tokio::time::{sleep, timeout};
use tonic;

#[derive(Debug, Clone)]
#[pyclass(get_all, set_all, name = "EtcdLockOption")]
pub struct PyEtcdLockOption {
    pub lock_name: String,
    pub timeout: Option<f64>,
    pub ttl: Option<i64>,
}

#[pymethods]
impl PyEtcdLockOption {
    #[new]
    fn new(lock_name: String, timeout: Option<f64>, ttl: Option<i64>) -> Self {
        Self {
            lock_name,
            timeout,
            ttl,
        }
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!(
            "EtcdLockOption(lock_name={}, timeout={:?}, ttl={:?})",
            self.lock_name, self.timeout, self.ttl
        ))
    }
}

pub struct EtcdLockManager {
    pub client: PyClient,
    pub lock_name: String,
    pub ttl: Option<i64>,
    pub timeout_seconds: Option<f64>,
    pub lock_id: Option<String>,
    pub lease_id: Option<i64>,
    pub lease_keepalive_task: Option<tokio::task::JoinHandle<()>>,
}

impl EtcdLockManager {
    pub fn new(client: PyClient, lock_opt: PyEtcdLockOption) -> Self {
        println!("lock_opt.ttl {:?}", lock_opt.ttl);
        println!("lock_opt.timeout {:?}", lock_opt.timeout);

        Self {
            client,
            lock_name: lock_opt.lock_name,
            ttl: lock_opt.ttl,
            timeout_seconds: lock_opt.timeout,

            lock_id: None,
            lease_id: None,
            lease_keepalive_task: None,
        }
    }

    // 지금 일단 막혀 있는 곳. 얘가 리턴을 안 함.
    pub async fn handle_aenter(&mut self) -> PyResult<PyCommunicator> {
        let client = self.client.clone();
        let mut client = EtcdClient::connect(client.endpoints, Some(client.options.0)).await.unwrap();

        let lock_name = self.lock_name.clone();

        println!("self.ttl {:?}", self.ttl);

        match self.ttl {
            Some(ttl) => {

                // TODO: Handle below err
                println!("Some ttl");
                let lease_res = client.lease_grant(ttl, None).await.unwrap();

                let mut client_to_move = client.clone();
                self.lease_keepalive_task = Some(tokio::spawn(async move {
                    // TODO: Handle below err
                    let (mut lease_keeper, _lease_stream) = client_to_move
                        .lease_keep_alive(lease_res.id())
                        .await
                        .unwrap();

                    loop {
                        sleep(Duration::from_secs((ttl / 10) as u64)).await;
                        // TODO: Handle below err
                        lease_keeper.keep_alive().await.unwrap();
                    }
                }));
                println!("Handle aenter! 3");
            }
            None => {
                println!("Lease id init");
                self.lease_id = None;
            }
        }

        println!("Handle aenter! middle");
        let timeout_result = timeout(
            Duration::from_secs_f64(self.timeout_seconds.unwrap()),
            async {
                let lock_res = client
                    .lock(lock_name.clone().as_bytes(), None)
                    .await
                    .unwrap();

                println!("try lock!!");
                self.lock_id = Some(std::str::from_utf8(lock_res.key()).unwrap().to_owned());
                println!("lock!! {:?}", self.lock_id);
            },
        )
        .await;

        if let Err(timedout_err) = timeout_result {
            println!("Timed out!");
            if self.lease_id.is_some() {
                match client.lease_revoke(self.lease_id.unwrap()).await {
                    Ok(_lease_revoke_res) => {}
                    Err(e) => {
                        match e {
                            etcd_client::Error::GRpcStatus(status)
                                if status.code() == tonic::Code::NotFound =>
                            {
                                ()
                            }
                            _ => return Err(PyClientError(e).into()),
                        }
                        return Err(LockError::new_err(timedout_err.to_string()).into());
                    }
                }
            }
            println!("Timed out 2");
            return Err(LockError::new_err(timedout_err.to_string()).into());
        }

        if self.lease_keepalive_task.is_some() {
            println!("abort!!");
            self.lease_keepalive_task.as_mut().unwrap().abort();
        }

        println!("Handle aenter finish");
        Ok(PyCommunicator::new(client))
    }

    pub async fn handle_aexit(&mut self) -> PyResult<()> {
        let client = self.client.clone();
        let mut client = EtcdClient::connect(client.endpoints, Some(client.options.0)).await.unwrap();

        println!("Handle aexit! start {:?}", self.lock_id);
        if self.lock_id.is_none() {
            return Err(PyClientError(etcd_client::Error::LockError(
                "Lock not acquired".to_owned(),
            ))
            .into());
        }

        println!("Handle aexit! 2");
        if self.lease_keepalive_task.is_some() {
            println!("Handle aexit! 3");
            self.lease_keepalive_task.as_ref().unwrap().abort();
        }

        if self.lease_id.is_some() {
            println!("Handle aexit! 4");
            // TODO: Handle below err
            client.lease_revoke(self.lease_id.unwrap()).await.unwrap();
        } else {
            println!("Handle aexit! 5");
            client
                .unlock(self.lock_id.to_owned().unwrap().as_bytes())
                .await
                .unwrap();
        }

        self.lock_id = None;
        self.lease_id = None;

        println!("Handle aexit! 6");
        Ok(())
    }
}
