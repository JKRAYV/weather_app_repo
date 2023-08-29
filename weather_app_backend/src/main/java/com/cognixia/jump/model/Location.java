package com.cognixia.jump.model;
import java.util.Objects;

public class Location {
    
    private Integer zipCode;


    public Location() {
    }

    public Location(Integer zipCode) {
        this.zipCode = zipCode;
    }

    public Integer getZipCode() {
        return this.zipCode;
    }

    public void setZipCode(Integer zipCode) {
        this.zipCode = zipCode;
    }

    public Location zipCode(Integer zipCode) {
        setZipCode(zipCode);
        return this;
    }

    @Override
    public boolean equals(Object o) {
        if (o == this)
            return true;
        if (!(o instanceof Location)) {
            return false;
        }
        Location location = (Location) o;
        return Objects.equals(zipCode, location.zipCode);
    }

    @Override
    public String toString() {
        return "{" +
            " zipCode='" + getZipCode() + "'" +
            "}";
    }
    
}
