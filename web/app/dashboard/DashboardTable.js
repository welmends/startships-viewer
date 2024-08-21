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
  const [data, setData] = useState([]);
  const [page, setPage] = useState(1);
  const [selectedfilter, setSelectedFilter] = useState("ALL");
  const [filter, setFilter] = useState("ALL");

  useEffect(() => {
    if (bearerToken) {
      const fetchData = async () => {
        setLoading(true);
        try {
          const response = await fetch(
            `${API_BASE_URL}/api/starships?page=${page}`,
            {
              method: "GET",
              headers: {
                Authorization: `Bearer ${bearerToken}`,
              },
            }
          );

          if (!response.ok) {
            if (response.status === 401) {
              setData(null);
              setError(response.statusText);
              router.push("/login");
              return;
            }
          }

          const data = await response.json();
          setData(data);
          setError(null);
        } catch (error) {
          setData(null);
          setError(error.message);
        } finally {
          setLoading(false);
        }
      };

      fetchData();
    }
  }, [bearerToken, page, selectedfilter]);

  useEffect(() => {
    if (error) {
      toast.error(`Error: ${error}`);
    }
  }, [error]);

  const handlePrevious = (event) => {
    event.preventDefault();
    if (data && data.previous) {
      setPage(page - 1);
    }
  };

  const handleNext = (event) => {
    event.preventDefault();
    if (data && data.next) {
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
              id="filter"
              className="select select-bordered w-full max-w-xs"
            >
              <option value="">All</option>
              <option value="category1">Category 1</option>
              <option value="category2">Category 2</option>
              <option value="category3">Category 3</option>
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
              {data &&
                data.results &&
                data.results.map((startship, index_row) => (
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
                disabled={data && data.previous === null}
              >
                Previous
              </button>
              <button
                id="next-page"
                className="btn btn-secondary ml-2"
                onClick={handleNext}
                disabled={data && data.next === null}
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
