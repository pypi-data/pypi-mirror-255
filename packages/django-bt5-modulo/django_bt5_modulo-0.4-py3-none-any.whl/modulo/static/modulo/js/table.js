export default class TableView extends HTMLElement {

    constructor() {
        super();
        this.attachShadow({mode: "open"});
    }

    connectedCallback() {
        this.shadowRoot.innerHTML = `
            <div class="table-responsive">
                <table class="table table-bordered">
                <thead class="table-light"></thead>
                <tbody></tbody>
                </table>
                <h1>hola mundo1</h1>
            </div>
        `;
    }

    /**
     *
     * @param head {string[]}
     */

    set headers(head) {

    }

    /**
     *
     * @param data {string[][]}
     */

    set data(data) {
        const tableBody = this.shadowRoot.querySelector('tbody');
        // const rows = document.map
        console.log(data)

    }
}