"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { API_BASE_URL } from "../constants";

const ROWS_PER_PAGE = 10;
const STARSHIP_ATTRS = {
  name: "Name",
  model: "Model",
  starship_class: "Class",
  manufacturer: "Manufacturer",
  cost_in_credits: "Cost (in credits)",
  length: "Length (meters)",
  crew: "Crew",
  passengers: "Passengers",
  max_atmosphering_speed: "Max Atmosphering Speed",
  hyperdrive_rating: "Hyperdrive Rating",
  MGLT: "MGLT",
  cargo_capacity: "Cargo Capacity (kg)",
  consumables: "Consumables",
};

const DashboardTable = ({ bearerToken }) => {
  const router = useRouter();
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [starshipsResponse, setStarshipsResponse] = useState(null);
  const [manufacturers, setManufacturers] = useState([]);
  const [selectedManufacturer, setSelectedManufacturer] = useState(undefined);

  useEffect(() => {
    if (error) {
      toast.error(`Error: ${error}`);
    }
  }, [error]);

  useEffect(() => {
    if (bearerToken) {
      let request_url = `${API_BASE_URL}/api/starships?page_size=${ROWS_PER_PAGE}&page=${page}`;
      if (selectedManufacturer !== undefined) {
        request_url += `&manufacturer=${selectedManufacturer}`;
      }

      const fetchStarships = async () => {
        setLoading(true);
        try {
          const response = await fetch(request_url, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${bearerToken}`,
            },
          });

          if (!response.ok) {
            if (response.status === 401) {
              setStarshipsResponse(null);
              setError(response.statusText);
              router.push("/login");
              return;
            }
          }

          const starships = await response.json();
          setStarshipsResponse(starships);
          setError(null);
        } catch (error) {
          setStarshipsResponse(null);
          setError(error.message);
        } finally {
          setLoading(false);
        }
      };

      fetchStarships();
    }
  }, [bearerToken, page, selectedManufacturer]);

  useEffect(() => {
    if (bearerToken) {
      const fetchManufacturers = async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/api/manufacturers`, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${bearerToken}`,
            },
          });

          if (!response.ok) {
            if (response.status === 401) {
              setManufacturers(null);
              setError(response.statusText);
              router.push("/login");
              return;
            }
          }

          const manufacturers = await response.json();
          setManufacturers(manufacturers);
          setError(null);
        } catch (error) {
          setManufacturers(null);
          setError(error.message);
        } finally {
          // should we add a different loading?
        }
      };

      fetchManufacturers();
    }
  }, [bearerToken]);

  const handleSelectedManufacturer = (event) => {
    event.preventDefault();
    if (event.target.value === "All") {
      setSelectedManufacturer(undefined);
      setPage(1);
    } else {
      setSelectedManufacturer(event.target.value);
      setPage(1);
    }
  };

  const handlePrevious = (event) => {
    event.preventDefault();
    if (starshipsResponse && starshipsResponse.previous) {
      setPage(page - 1);
    }
  };

  const handleNext = (event) => {
    event.preventDefault();
    if (starshipsResponse && starshipsResponse.next) {
      setPage(page + 1);
    }
  };

  return (
    <div className="overflow-x-auto">
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      ) : (
        <div>
          <div className="flex justify-end items-center mb-4">
            <select
              id="selectedManufacturer"
              value={selectedManufacturer}
              className="select select-bordered w-full max-w-xs"
              onChange={handleSelectedManufacturer}
            >
              <option value="All">All</option>
              {manufacturers &&
                manufacturers.results &&
                manufacturers.results.map((manufacturer, index) => (
                  <option key={index} value={manufacturer}>
                    {manufacturer}
                  </option>
                ))}
            </select>
          </div>

          <table className="table min-w-full divide-y">
            <thead>
              <tr>
                <th>#</th>
                {Object.values(STARSHIP_ATTRS).map((name, index) => (
                  <th key={index}>{name}</th>
                ))}
              </tr>
            </thead>
            <tbody id="table-body">
              {starshipsResponse &&
                starshipsResponse.results &&
                starshipsResponse.results.map((startship, index_row) => (
                  <tr key={index_row}>
                    <th>{(page - 1) * ROWS_PER_PAGE + (index_row + 1)}</th>
                    {Object.keys(STARSHIP_ATTRS).map((name, index_elem) => (
                      <td key={index_elem}>{startship[name] || "-"}</td>
                    ))}
                  </tr>
                ))}
            </tbody>
          </table>

          <div className="flex justify-end items-center mt-4">
            <div className="pagination">
              <button
                id="prev-page"
                className="btn btn-secondary"
                onClick={handlePrevious}
                disabled={
                  starshipsResponse && starshipsResponse.previous === null
                }
              >
                Previous
              </button>
              <button
                id="next-page"
                className="btn btn-secondary ml-2"
                onClick={handleNext}
                disabled={starshipsResponse && starshipsResponse.next === null}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
      <ToastContainer />
    </div>
  );
};

export default DashboardTable;
