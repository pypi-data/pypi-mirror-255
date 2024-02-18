import ListaView from "./lista.min.js";

class Modelo {

    constructor() {
        this.csrftoken = this.getCookie('csrftoken');
        HTMLElement.prototype.showloader = function loadingShow() {
            let html = `
                    
<!--                        <div style="" class="position-fixed text-center bg-white">-->
              <div  style="z-index: 1000;top: 0; left: 0; right: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.53); position: fixed">
                <div class="position-fixed top-50 start-50 translate-middle" style="z-index: 1001;  ">
                     <div class="spinner-grow text-primary" style="width: 3rem; height: 3rem;" role="status">
                      <span class="visually-hidden">Loading...</span>
                    </div>
<!--                            <img src="/static/mazer/assets/vendors/svg-loaders/circles.svg" class="me-4 " style="width: 3rem" alt="audio">-->

                </div>                                
               </div>
            `;
            let createDiv = document.createElement("div");
            createDiv.classList.add('loading');
            createDiv.innerHTML = html;
            this.append(createDiv);
        }

        HTMLElement.prototype.hideloader = function loadingHiden() {
            let element = document.querySelector(".loading");
            if (element) {
                element.remove();
            }
        }
    }

    async onSubmit(ev, element, formulario, modal) {
        ev.preventDefault();
        if (modal) {
            element = modal.querySelector(".modal-content");
        }
        element.showloader();
        const formdata = new FormData(formulario);
        try {
            let res = await fetch(formulario.getAttribute('action'), {
                method: "POST", body: formdata,
            })
            if (res.ok) {
                let resultado = await res.text();
                try {
                    resultado = JSON.parse(resultado);
                    this.toastShow(document.getElementById("toastLoading"), resultado.mensaje, {
                        ms: 3000, bg: resultado.success ? "bg-success" : "bg-danger"
                    });
                    if (modal) {
                        let modal_instance = bootstrap.Modal.getInstance(modal);
                        modal_instance.hide();
                    }
                    element.hideloader();
                    return {
                        estado: true, valor: resultado
                    }
                } catch (e) {
                    element.hideloader();
                    if (modal) {
                        modal.querySelector(".modal-body").innerHTML = resultado;
                    }
                    return {
                        estado: false, valor: resultado
                    }
                }
            } else {
                element.hideloader();
                this.toastShow(document.getElementById("toastLoading"), "Error", {
                    ms: 3000, bg: "bg-danger"
                });
                return {
                    estado: false, valor: await res.text()
                }
            }

        } catch (err) {
            element.hideloader();
            this.toastShow(document.getElementById("toastLoading"), "Error", {
                ms: 3000, bg: "bg-danger"
            });
            return {
                estado: false, valor: null
            }
        }
    }

    async getUrlContenedor(url, element) {
        element.showloader();
        await fetch(url)
            .then(response => {
                if (response.ok) {
                    return response.text()
                } else {
                    throw new Error('Error')
                }
            })
            .then(response => {
                // console.log('Success:', response);
                element.innerHTML = response;
                element.hideloader();
            }).catch(error => {
                element.hideloader();
                throw new Error('Error')
            });
    }

    async getUrlContenedorNoLoad(url, element) {
        await fetch(url)
            .then(response => response.text())
            .catch((error) => {
                console.error('Error:', error)
            })
            .then((response) => {
                // console.log('Success:', response);
                element.innerHTML = response;
            }).catch(() => {
            });
    }

    async getPostObjectJson(url = '', data = new FormData, element) {
        element.showloader()
        const resultado = await fetch(url, {
            headers: {'X-CSRFToken': this.csrftoken}, method: "POST", body: data, mode: 'same-origin'
        });
        if (resultado.ok) {
            element.hideloader()
        } else {
            element.hideloader()
        }
        return resultado.json();
    }

    async getGetObjectJson(url = '') {
        const resultado = await fetch(url, {
            method: "GET", headers: {
                'Content-Type': 'application/json'
            }
        });
        return await resultado.json();
    }

    async submit_event(ev, element, formulario, f) {
        ev.preventDefault();
        element.showloader();
        const formdata = new FormData(formulario);
        try {
            let res = await fetch(formulario.getAttribute('action'), {
                method: "POST", body: formdata,
            })
            if (res.ok) {
                const resultado = await res.text();
                f(resultado);
            }
            element.hideloader();
        } catch (err) {
            console.log(err)
            element.hideloader();
        }
    }

    toastShow(element, texto, options = {}) {
        let ms = options.ms !== undefined ? options.ms : 1000;
        let bg = options.bg !== undefined ? options.bg : "bg-success"
        var toast = new bootstrap.Toast(element, {
            'animation': true, 'delay': ms ? ms : 2000,
        });
        element.classList.remove("bg-success");
        element.classList.remove("bg-danger");
        element.classList.remove("bg-primary");
        element.classList.remove("bg-warning");
        element.classList.remove("bg-secondary");
        element.classList.add(bg);
        element.querySelector(".toast-body").innerHTML = texto;
        toast.show()
    }

    async openModal(element_modal, formulario, url = '', titulo = "", options = {}) {
        let modal = new bootstrap.Modal(element_modal, options ? options : {});
        element_modal.querySelector('.modal-content').showloader();
        formulario.setAttribute("action", url);
        formulario.setAttribute("method", "post");
        element_modal.querySelector(".modal-title").innerHTML = titulo;
        let response = await fetch(url);
        if (response.ok) {
            element_modal.querySelector(".modal-body").innerHTML = await response.text();
            modal.show();
            element_modal.hideloader();
        }
        element_modal.querySelector('.modal-content').hideloader();
    }

    open_modal_single(modal_element, titulo, cuerpo, tamanio = '') {
        if (tamanio) {
            modal_element.querySelector(".modal-dialog").classList.add(`modal-${tamanio}`);
        }
        const options = {}
        let modal = new bootstrap.Modal(modal_element, options ? options : {});
        modal_element.querySelector(".modal-title").innerHTML = titulo;
        modal_element.querySelector(".modal-footer").classList.add('d-none')
        modal_element.querySelector(".modal-body").innerHTML = null
        modal_element.querySelector(".modal-body").append(cuerpo);
        modal.show();
        modal_element.addEventListener('hidden.bs.modal', event => {
            modal_element.querySelector(".modal-footer").classList.remove('d-none');
            if (tamanio) {
                modal_element.querySelector(".modal-dialog").classList.remove(`modal-${tamanio}`);
            }
        })

    }

    AlertView(element, message, type) {
        var wrapper = document.createElement('div')
        wrapper.innerHTML = '<div class="modulo-alert alert alert-' + type + ' alert-dismissible" role="alert">' + message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>'
        element.append(wrapper)
    }

    get_socket(url) {
        return new WebSocket('' + (window.location.protocol === "https:" ? "wss" : "ws") + '://' + window.location.host + url);

    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    off_canvas_load(url, titulo, options = {}) {
        if (Object.entries(options).length === 0) {
            options = {
                backdrop: true, keyboard: false, scroll: false
            }
        }
        const offcanvas = document.getElementById('offcanvasGeneral');

        const bsOffcanvas = new bootstrap.Offcanvas(offcanvas, options);

        offcanvas.querySelector(".offcanvas-title").textContent = titulo;
        // this.getUrlContenedor(url, offcanvas.querySelector(".offcanvas-body")).then(() => {
        //     bsOffcanvas.show();
        // });
        bsOffcanvas.toggle();
        return new ListaView(this, offcanvas.querySelector(".offcanvas-body"), url)

    }

    off_canvas_close() {
        const offcanvas = document.getElementById('offcanvasGeneral');
        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvas);
        bsOffcanvas.hide();
    }
}

export default Modelo;

export function ajax_select2(url) {
    return {
        url: url, data: function (params) {
            // Query parameters will be ?search=[term]&page=[page]
            return {
                search: params.term, page: params.page || 1
            };
        }
    }
}


export function seleccionar_menu() {
    let navs = document.querySelectorAll(".nav-link");
    navs.forEach(element => {
        if (window.location.pathname === element.getAttribute("href")) {
            element.classList.remove('active')
            element.classList.add('active')
        }
    });
}