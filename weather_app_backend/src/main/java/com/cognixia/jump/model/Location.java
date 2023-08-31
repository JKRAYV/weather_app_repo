package com.cognixia.jump.model;
import java.util.Objects;

public class Location {
    
    private String town;

    private Integer zipCode;


    public Location() {
    }

    public Location(String town, Integer zipCode) {
        this.town = town;
        this.zipCode = zipCode;
    }

    public String getTown() {
        return this.town;
    }

    public void setTown(String town) {
        this.town = town;
    }

    public Integer getZipCode() {
        return this.zipCode;
    }

    public void setZipCode(Integer zipCode) {
        this.zipCode = zipCode;
    }

    public Location town(String town) {
        setTown(town);
        return this;
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
        return Objects.equals(town, location.town) && Objects.equals(zipCode, location.zipCode);
    }

    @Override
    public int hashCode() {
        return Objects.hash(town, zipCode);
    }

    @Override
    public String toString() {
        return "{" +
            " town='" + getTown() + "'" +
            ", zipCode='" + getZipCode() + "'" +
            "}";
    }
    
}
