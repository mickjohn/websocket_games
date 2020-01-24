import React from 'react';
import './modal.css';

interface Props {
    children: React.ReactNode;
    className?: string;
    closeModal?: () => void;
}


class Modal extends React.Component<Props>   {

    constructor(props: Props) {
        super(props);
    }

    render() {
        let classes = "modal modal-main";
        if (this.props.className !== undefined) {
            classes += ` ${this.props.className}`;
        }
        return (
            <div className="modal" onClick={(e) => this.tryCloseModal(e)}>
                <div className={classes} onClick={(e) => this.modalContentClicked(e)}>
                    {this.props.children}
                </div>
            </div>
        );
    }

    /*
    Prevent a click on the modal content from propagating up to the 'modal'
    class (which would cause the modal to close).
    */
    modalContentClicked(event: any) {
        event.preventDefault();
        event.stopPropagation();
    }

    tryCloseModal(event: any) {
        if (this.props.closeModal !== undefined) {
            this.props.closeModal();
        }
    }

}

export default Modal;