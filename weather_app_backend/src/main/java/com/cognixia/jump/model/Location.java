package com.cognixia.jump.model;
import java.util.Objects;

public class Location {
    
    private String town;

    private Integer zip;


    public Location() {
    }

    public Location(String town, Integer zip) {
        this.town = town;
        this.zip = zip;
    }

    public String getTown() {
        return this.town;
    }

    public void setTown(String town) {
        this.town = town;
    }

    public Integer getZip() {
        return this.zip;
    }

    public void setZip(Integer zip) {
        this.zip = zip;
    }

    public Location town(String town) {
        setTown(town);
        return this;
    }

    public Location zip(Integer zip) {
        setZip(zip);
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
        return Objects.equals(town, location.town) && Objects.equals(zip, location.zip);
    }

    @Override
    public int hashCode() {
        return Objects.hash(town, zip);
    }

    @Override
    public String toString() {
        return "{" +
            " town='" + getTown() + "'" +
            ", zip='" + getZip() + "'" +
            "}";
    }


}
