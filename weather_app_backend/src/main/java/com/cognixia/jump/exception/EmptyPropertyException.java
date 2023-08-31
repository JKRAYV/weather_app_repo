package com.cognixia.jump.exception;

public class EmptyPropertyException extends Exception {
    
    private static final long serialVersionUID = 1L;

    public EmptyPropertyException(String resource) {
        super(resource + "was not found");
    }
}
