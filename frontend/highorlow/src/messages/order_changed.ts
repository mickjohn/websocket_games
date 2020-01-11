import Player from '../player';

class OrderChanged {
    static msgtype = "OrderChanged";
    order: Player[];

    constructor(order: Player[]) {
        this.order = order;
    }

    static fromJson(msg: any): OrderChanged | null {
        const order: Player[] = msg['order'];

        return new OrderChanged(order);
    }
}

export default OrderChanged;
