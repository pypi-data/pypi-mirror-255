use crate::{communicator::PyCommunicator, error::{LockError, PyClientError}};
use etcd_client::Client as EtcdClient;
use pyo3::prelude::*;
use std::time::Duration;
use tokio::time::{sleep, timeout};
use tonic;

#[derive(Clone)]
#[pyclass(get_all, set_all, name = "EtcdLockOption")]
pub struct PyEtcdLockOption {
    pub lock_name: String,
    pub timeout: Option<f64>,
    pub ttl: Option<i64>,
}

pub struct EtcdLockManager {
    pub client: EtcdClient,
    pub lock_name: String,
    pub ttl: Option<i64>,
    pub timeout_seconds: Option<f64>,
    pub lock_id: Option<String>,
    pub lease_id: Option<i64>,
    pub lease_keepalive_task: Option<tokio::task::JoinHandle<()>>,
}

impl EtcdLockManager {
    pub fn new(client: EtcdClient, lock_opt: PyEtcdLockOption) -> Self {
        Self {
            client,
            lock_name: lock_opt.lock_name,
            ttl: lock_opt.ttl,
            timeout_seconds: lock_opt.timeout,
            lease_id: None,
            lock_id: None,
            lease_keepalive_task: None,
        }
    }

    // 지금 일단 막혀 있는 곳. 얘가 리턴을 안 함.
    pub async fn handle_aenter(&mut self) -> PyResult<PyCommunicator> {
        let mut client = self.client.clone();
        let lock_name = self.lock_name.clone();

        match self.ttl {
            Some(ttl) => {
                // TODO: Handle below err
                let lease_res = client.lease_grant(ttl, None).await.unwrap();

                let mut client_to_move = client.clone();
                println!("Handle aenter! 2");
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
                self.lease_id = None;
            }
        }

        println!("Handle aenter! 4");
        let timeout_result = timeout(
            Duration::from_secs_f64(self.timeout_seconds.unwrap()),
            async {
                let lock_res = client
                    .lock(lock_name.clone().as_bytes(), None)
                    .await
                    .unwrap();

                self.lock_id = Some(std::str::from_utf8(lock_res.key()).unwrap().to_owned());
            },
        )
        .await;

        println!("Handle aenter! 5");

        if let Err(timedout_err) = timeout_result {
            println!("Handle aenter! 6");
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
            println!("Handle aenter! 7");
            return Err(LockError::new_err(timedout_err.to_string()).into());
        }

        println!("Handle aenter! 8");
        if self.lease_keepalive_task.is_some() {
            self.lease_keepalive_task.as_mut().unwrap().abort();
        }
        
        println!("Handle aenter! 9");
        Ok(PyCommunicator::new(client))
    }

    pub async fn handle_aexit(&mut self) -> PyResult<()> {
        if self.lock_id.is_none() {
            return Err(PyClientError(etcd_client::Error::LockError(
                "Lock not acquired".to_owned(),
            ))
            .into());
        }

        if self.lease_keepalive_task.is_some() {
            self.lease_keepalive_task.as_ref().unwrap().abort();
        }

        let mut client = self.client.clone();

        if self.lease_id.is_some() {
            // TODO: Handle below err
            client.lease_revoke(self.lease_id.unwrap()).await.unwrap();
        } else {
            client
                .unlock(self.lock_id.to_owned().unwrap().as_bytes())
                .await
                .unwrap();
        }

        self.lock_id = None;
        self.lease_id = None;

        Ok(())
    }
}
