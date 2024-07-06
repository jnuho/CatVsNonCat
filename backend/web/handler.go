package web

import (
	"log"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func getMethodHandler(c *gin.Context) {
	c.String(http.StatusOK, "OK")
}

func catPostHandler(c *gin.Context) {
	startNow := time.Now()
	catObj, err := validateRequest(c)
	if err != nil {
		log.Println("Validation error: ", err)
		c.JSON(http.StatusBadRequest, gin.H{
			"message": err.Error(),
		})
		return
	}

	result, err := callPythonBackend(catObj.URL)
	if err != nil {
		log.Println("Python backend call error:", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"message": "Error calling Python backend",
		})
		return
	}

	duration := time.Since(startNow).Seconds()
	c.JSON(http.StatusOK, gin.H{
		"cat_url":       result.URL,
		"go_server":     "ok",
		"python_server": result.STATUS,
		"elapsed":       duration,
		// "python_server": result.STATUS,
	})
}

func weatherPostHandler(c *gin.Context) {

	startNow := time.Now()

	list, err := callWeatherAPi()

	duration := time.Since(startNow).Seconds()
	log.Printf("\nThis operation took: %v\n\n", duration)

	if err != nil {
		log.Println("WeatherApi call error:", err)
		c.JSON(http.StatusInternalServerError, gin.H{
			"message": "Error calling GetWeatherInfo()",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"weather_list": list,
		"elapsed":      duration,
	})
}
