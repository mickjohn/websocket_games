
class ErrorMessage {
    static msgtype = "ErrorMessage";
    errorType: string;
    msg: string;

    constructor(msg: string, errorType: string) {
        this.msg = msg;
        this.errorType = errorType;
    }

    static fromJson(msg: any): ErrorMessage | null {
        const error: ErrorMessage = msg;
        return error;
    }
}

export default ErrorMessage;